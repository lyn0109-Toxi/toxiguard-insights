class App {
    constructor() {
        this.apiKey = localStorage.getItem('finnhub_api_key') || 'd7oo6ghr01qsb7bfl340d7oo6ghr01qsb7bfl34g';
        this.riskFreeRate = parseFloat(localStorage.getItem('risk_free_rate')) || 4.50;
        this.equityRiskPremium = parseFloat(localStorage.getItem('equity_risk_premium')) || 4.50;
        
        // Load cached stocks for instant display
        const cached = localStorage.getItem('cached_stocks');
        this.stocks = cached ? JSON.parse(cached) : []; 
        
        this.selectedStocks = new Set();
        this.currentFilter = 'all';
        this.ws = null;
        this.portfolio = JSON.parse(localStorage.getItem('user_portfolio')) || {}; // { symbol: { shares: 10, costBasis: 100 } }
        this.portfolioSort = { key: 'weight', direction: 'desc' };
        this.sectorChart = null;
        
        // DOM Elements
        this.stockGrid = document.getElementById('stock-grid');
        this.searchInput = document.getElementById('search-input');
        this.loadingIndicator = document.getElementById('loading-indicator');
        this.filterBtns = document.querySelectorAll('.filter-btn');
        
        // Navigation & Modals
        this.navSearch = document.getElementById('nav-search');
        this.navCompare = document.getElementById('nav-compare');
        this.navPortfolio = document.getElementById('nav-portfolio');
        this.navSettings = document.getElementById('nav-settings');
        this.sectionSearch = document.getElementById('section-search');
        this.sectionCompare = document.getElementById('section-compare');
        this.sectionPortfolio = document.getElementById('section-portfolio');
        this.sectionDetail = document.getElementById('section-detail');
        this.compareBadge = document.getElementById('compare-badge');
        this.goToSearchBtn = document.getElementById('go-to-search-btn');
        this.backToSearchBtn = document.getElementById('back-to-search');
        this.detailContent = document.getElementById('detail-content');
        
        // Portfolio Elements
        this.portfolioBody = document.getElementById('portfolio-body');
        this.emptyPortfolio = document.getElementById('empty-portfolio');
        this.portfolioTotalValue = document.getElementById('portfolio-total-value');
        this.portfolioWeightedBeta = document.getElementById('portfolio-weighted-beta');
        this.portfolioValuationScore = document.getElementById('portfolio-valuation-score');
        
        // Settings Modal
        this.settingsModal = document.getElementById('settings-modal');
        this.closeSettingsBtn = document.getElementById('close-settings');
        this.apiKeyInput = document.getElementById('api-key-input');
        this.saveApiKeyBtn = document.getElementById('save-api-key');
        this.riskFreeRateInput = document.getElementById('risk-free-rate');
        this.equityRiskPremiumInput = document.getElementById('equity-risk-premium');
        this.syncMacroBtn = document.getElementById('sync-macro-btn');
        this.syncStatus = document.getElementById('sync-status');

        // Compare Elements
        this.emptyCompare = document.getElementById('empty-compare');
        this.compareTableWrapper = document.getElementById('compare-table-wrapper');
        this.compareHeader = document.getElementById('compare-header');
        this.compareBody = document.getElementById('compare-body');

        // CAPM Modal Elements
        this.capmModal = document.getElementById('capm-modal');
        this.closeModalBtn = document.getElementById('close-modal');
        this.capmModalBody = document.getElementById('capm-modal-body');

        this.init();
    }

    async init() {
        this.bindEvents();
        if (this.riskFreeRateInput) {
            this.riskFreeRateInput.value = this.riskFreeRate.toFixed(2);
            this.equityRiskPremiumInput.value = this.equityRiskPremium.toFixed(2);
        }
        if (this.apiKey) {
            this.apiKeyInput.value = this.apiKey;
            
            // Render cached stocks immediately
            if (this.stocks.length > 0) {
                this.renderStocks();
                console.log("Loaded stocks from cache.");
            } else {
                await this.loadDefaultStocks();
            }

            // Check if macro data needs sync (older than 12 hours)
            const lastSync = localStorage.getItem('last_macro_sync');
            const now = Date.now();
            if (!lastSync || (now - parseInt(lastSync)) > 12 * 60 * 60 * 1000) {
                console.log("Macro cache expired. Syncing...");
                this.syncMacroData();
            }

            this.setupWebSocket();
        } else {
            this.stockGrid.innerHTML = `
                <div class="empty-state" style="grid-column: 1/-1">
                    <p>A Finnhub API Key is required. Click the Settings (⚙️) icon above to enter your key.</p>
                </div>
            `;
        }
    }

    bindEvents() {
        // Navigation
        this.navSearch.addEventListener('click', () => this.switchTab('search'));
        this.navCompare.addEventListener('click', () => this.switchTab('compare'));
        this.navPortfolio.addEventListener('click', () => this.switchTab('portfolio'));
        this.goToSearchBtn.addEventListener('click', () => this.switchTab('search'));
        this.backToSearchBtn.addEventListener('click', () => this.switchTab('search'));
        
        const exportBtn = document.getElementById('export-portfolio-csv');
        if (exportBtn) exportBtn.addEventListener('click', () => this.exportPortfolioToCSV());

        document.querySelectorAll('.holdings-table th.sortable').forEach(th => {
            th.addEventListener('click', () => this.sortPortfolio(th.dataset.sort));
        });

        this.navSettings.addEventListener('click', () => this.settingsModal.classList.remove('hidden'));

        // Settings Modal
        this.closeSettingsBtn.addEventListener('click', () => this.settingsModal.classList.add('hidden'));
        this.saveApiKeyBtn.addEventListener('click', () => {
            const val = this.apiKeyInput.value.trim();
            if (val) {
                localStorage.setItem('finnhub_api_key', val);
                this.apiKey = val;
                this.settingsModal.classList.add('hidden');
                this.init(); // Reload
            }
        });

        if (this.riskFreeRateInput) {
            this.riskFreeRateInput.addEventListener('change', (e) => {
                this.riskFreeRate = parseFloat(e.target.value) || 4.50;
                localStorage.setItem('risk_free_rate', this.riskFreeRate);
                this.recalculateAll();
            });
        }

        if (this.equityRiskPremiumInput) {
            this.equityRiskPremiumInput.addEventListener('change', (e) => {
                this.equityRiskPremium = parseFloat(e.target.value) || 4.50;
                localStorage.setItem('equity_risk_premium', this.equityRiskPremium);
                this.recalculateAll();
            });
        }

        if (this.syncMacroBtn) {
            this.syncMacroBtn.addEventListener('click', () => this.syncMacroData());
        }

        // CAPM Modal
        this.closeModalBtn.addEventListener('click', () => this.capmModal.classList.add('hidden'));
        this.capmModal.addEventListener('click', (e) => {
            if (e.target === this.capmModal) this.capmModal.classList.add('hidden');
        });

        // Live Search via Finnhub
        let searchTimeout;
        this.searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const query = e.target.value.toUpperCase().trim();
                if (query) {
                    this.fetchStockData(query);
                }
            }
        });

        // Filter events
        if (this.filterBtns) {
            this.filterBtns.forEach(btn => {
                btn.addEventListener('click', (e) => {
                    this.filterBtns.forEach(b => b.classList.remove('active'));
                    const target = e.currentTarget;
                    target.classList.add('active');
                    this.currentFilter = target.dataset.filter;
                    this.renderStocks();
                });
            });
        }
    }

    async loadDefaultStocks() {
        this.loadingIndicator.classList.remove('hidden');
        this.stockGrid.innerHTML = '';
        const defaultTickers = ['AAPL', 'TSLA', 'PFE'];
        
        let hasError = false;
        for (const ticker of defaultTickers) {
            const success = await this.fetchStockData(ticker, false, true); // isDefault = true
            if (!success) hasError = true;
        }
        this.loadingIndicator.classList.add('hidden');
        
        if (hasError && this.stocks.length === 0) {
            this.stockGrid.innerHTML = `
                <div class="empty-state" style="grid-column: 1/-1">
                    <p>Failed to load default stock data. Please check if your API key is valid.</p>
                </div>
            `;
        } else {
            this.renderStocks();
        }
    }

    async resolveTicker(query) {
        try {
            const res = await fetch(`https://finnhub.io/api/v1/search?q=${encodeURIComponent(query)}&token=${this.apiKey}`);
            if (res.ok) {
                const data = await res.json();
                if (data.result && data.result.length > 0) {
                    const results = data.result;
                    const upperQuery = query.toUpperCase();

                    // 1. Exact Ticker Match (e.g. "PFE")
                    const exactTicker = results.find(r => r.symbol === upperQuery);
                    if (exactTicker) return exactTicker.symbol;

                    // 2. Filter for Common Stocks
                    const commonStocks = results.filter(r => r.type === 'Common Stock');
                    const targetList = commonStocks.length > 0 ? commonStocks : results;

                    // 3. Prefer US Exchanges (Symbols without dots like PFE, AAPL)
                    const usStocks = targetList.filter(r => !r.symbol.includes('.'));
                    if (usStocks.length > 0) {
                        // Among US stocks, pick the one where description starts with query
                        const startsWithMatch = usStocks.find(r => r.description.toUpperCase().startsWith(upperQuery));
                        return startsWithMatch ? startsWithMatch.symbol : usStocks[0].symbol;
                    }

                    // 4. Fallback to first result
                    return targetList[0].symbol;
                }
            }
        } catch (e) { console.error("Search API error", e); }
        return query.toUpperCase();
    }

    async fetchStockData(query, renderImmediate = true, isDefault = false) {
        if (!this.apiKey) return false;

        if (renderImmediate) {
            this.loadingIndicator.classList.remove('hidden');
        }

        // Auto-resolve ticker if it's a company name
        let ticker = query.toUpperCase();
        if (!isDefault) {
            ticker = await this.resolveTicker(query);
        }
        
        // Prevent duplicate fetching if already exists
        if (this.stocks.find(s => s.id === ticker)) {
            if (renderImmediate) {
                this.loadingIndicator.classList.add('hidden');
                this.renderStocks();
            }
            return true;
        }

        try {
            // Fetch Profile, Quote, Metric, and Peers in parallel
            const [profileRes, quoteRes, metricRes, peersRes] = await Promise.all([
                fetch(`https://finnhub.io/api/v1/stock/profile2?symbol=${ticker}&token=${this.apiKey}`),
                fetch(`https://finnhub.io/api/v1/quote?symbol=${ticker}&token=${this.apiKey}`),
                fetch(`https://finnhub.io/api/v1/stock/metric?symbol=${ticker}&metric=all&token=${this.apiKey}`),
                fetch(`https://finnhub.io/api/v1/stock/peers?symbol=${ticker}&token=${this.apiKey}`)
            ]);

            if (!profileRes.ok || !quoteRes.ok) {
                throw new Error("API request failed: Please check your API key or network.");
            }

            const profile = await profileRes.json();
            const quote = await quoteRes.json();
            
            // Handle cases where response might be text or empty for metrics
            let metricData = {};
            let peers = [];
            try { metricData = await metricRes.json(); } catch(e) {}
            try { peers = await peersRes.json(); } catch(e) {}
            
            const metric = metricData.metric || {};

            let peerPEs = [];
            const topPeers = Array.isArray(peers) ? peers.filter(p => p !== ticker).slice(0, 3) : [];
            
            if (topPeers.length > 0) {
                try {
                    const peerPromises = topPeers.map(p => fetch(`https://finnhub.io/api/v1/stock/metric?symbol=${p}&metric=all&token=${this.apiKey}`).then(r => r.json()));
                    const peerDataList = await Promise.all(peerPromises);
                    
                    peerDataList.forEach(pData => {
                        if (pData && pData.metric) {
                            const pe = pData.metric.peExclExtraTTM || pData.metric.peBasicExclExtraTTM;
                            if (pe && pe > 0 && pe < 150) { // filter out absurd P/Es
                                peerPEs.push(pe);
                            }
                        }
                    });
                } catch(e) {
                    console.warn("Failed to fetch peer metrics", e);
                }
            }
            
            // Default to 15 if no peers or no valid P/E ratios found
            const avgPeerPE = peerPEs.length > 0 ? peerPEs.reduce((a, b) => a + b, 0) / peerPEs.length : 15;

            const currentPrice = quote.c || 0;
            // Fallback: If no current price, data is completely invalid
            if (currentPrice === 0) {
                if (!isDefault) alert(`No stock data found for '${query}'. Please enter a valid name or ticker.`);
                if (renderImmediate) this.loadingIndicator.classList.add('hidden');
                return false;
            }

            const priceChangePct = quote.dp || 0;
            const isPositive = priceChangePct > 0;
            
            const newStock = {
                id: ticker,
                name: profile.name || query.toUpperCase(),
                type: profile.finnhubIndustry || "ETF / Other",
                price: currentPrice,
                previousPrice: currentPrice, // To track real-time changes
                change: (isPositive ? '+' : '') + priceChangePct.toFixed(2) + '%',
                marketCap: profile.marketCapitalization ? (profile.marketCapitalization / 1000).toFixed(2) + 'B' : 'N/A',
                per: metric.peExclExtraTTM ? metric.peExclExtraTTM.toFixed(2) : (metric.peBasicExclExtraTTM ? metric.peBasicExclExtraTTM.toFixed(2) : 'N/A'),
                dividendYield: metric.dividendYieldIndicatedAnnual ? metric.dividendYieldIndicatedAnnual.toFixed(2) + '%' : '0%',
                pipelineCount: "N/A", 
                description: profile.name ? `${profile.name} (${profile.ticker}) belongs to the ${profile.finnhubIndustry || 'General'} sector.` : `${ticker} — Limited financial data available (Free API restriction).`,
                beta: metric.beta || 1.0, // Fallback
                eps: metric.epsExclExtraItemsTTM || metric.epsBasicExclExtraItemsTTM || 0, // Fallback
                dividend: metric.dividendPerShareAnnual || 0, // Fallback
                growthRate: (metric.epsGrowth3Y || 5) / 100, // Convert to decimal
                bookValue: metric.bookValuePerShareAnnual || 0, // For Graham Number
                peers: topPeers,
                peerAveragePE: avgPeerPE
            };

            this.calculateValuation(newStock);
            this.stocks.unshift(newStock); // Add to top
            
            // Keep only last 10 stocks in cache to prevent storage bloat
            const cacheLimit = 10;
            const stockCache = this.stocks.slice(0, cacheLimit);
            localStorage.setItem('cached_stocks', JSON.stringify(stockCache));
            
            // Subscribe to real-time updates for new ticker
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify({'type': 'subscribe', 'symbol': ticker}));
            }

            if (renderImmediate) {
                this.loadingIndicator.classList.add('hidden');
                this.renderStocks();
            }
            return true;

        } catch (error) {
            console.error("Error fetching stock:", error);
            if (!isDefault) alert("An error occurred while fetching data. Please check if your API key is valid.");
            if (renderImmediate) this.loadingIndicator.classList.add('hidden');
            return false;
        }
    }

    setupWebSocket() {
        if (!this.apiKey) return;
        
        if (this.ws) {
            this.ws.close();
        }

        this.ws = new WebSocket(`wss://ws.finnhub.io?token=${this.apiKey}`);

        this.ws.onopen = () => {
            // Subscribe to currently loaded stocks
            this.stocks.forEach(stock => {
                this.ws.send(JSON.stringify({'type': 'subscribe', 'symbol': stock.id}));
            });
        };

        this.ws.onmessage = (event) => {
            const response = JSON.parse(event.data);
            if (response.type === 'trade' && response.data) {
                // Process only the latest trade for each symbol
                const latestTrades = {};
                response.data.forEach(trade => {
                    latestTrades[trade.s] = trade.p;
                });

                let needsRender = false;
                Object.keys(latestTrades).forEach(symbol => {
                    const stock = this.stocks.find(s => s.id === symbol);
                    if (stock && stock.price !== latestTrades[symbol]) {
                        stock.previousPrice = stock.price;
                        stock.price = latestTrades[symbol];
                        this.calculateValuation(stock);
                        needsRender = true;
                    }
                });

                if (needsRender) {
                    this.updatePricesInDOM();
                }
            }
        };
    }

    recalculateAll() {
        this.stocks.forEach(stock => this.calculateValuation(stock));
        this.renderStocks();
        if (this.sectionCompare.classList.contains('active')) {
            this.renderCompareTable();
        }
    }

    async syncMacroData() {
        if (!this.syncMacroBtn) return;
        
        this.syncMacroBtn.disabled = true;
        this.syncMacroBtn.innerHTML = `<i data-lucide="loader" class="spin"></i> Syncing...`;
        this.syncStatus.textContent = "Fetching live market data...";
        this.syncStatus.style.color = "var(--text-secondary)";
        lucide.createIcons();

        try {
            const [tnxYield, erp] = await Promise.all([
                this.fetchTreasuryYield(),
                this.fetchDamodaranERP()
            ]);

            let successMsg = [];
            if (tnxYield) {
                this.riskFreeRate = tnxYield;
                this.riskFreeRateInput.value = tnxYield.toFixed(2);
                localStorage.setItem('risk_free_rate', this.riskFreeRate);
                successMsg.push(`Risk-Free: ${tnxYield.toFixed(2)}%`);
            }
            if (erp) {
                this.equityRiskPremium = erp;
                this.equityRiskPremiumInput.value = erp.toFixed(2);
                localStorage.setItem('equity_risk_premium', this.equityRiskPremium);
                successMsg.push(`ERP: ${erp.toFixed(2)}%`);
            }

            if (successMsg.length > 0) {
                this.syncStatus.textContent = `✅ Synced: ${successMsg.join(', ')}`;
                this.syncStatus.style.color = "var(--valuation-under)";
                localStorage.setItem('last_macro_sync', Date.now().toString());
                this.recalculateAll();
            } else {
                throw new Error("Could not fetch data.");
            }
        } catch (error) {
            console.error("Macro Sync Error:", error);
            this.syncStatus.textContent = "❌ Failed to fetch data. Try again later.";
            this.syncStatus.style.color = "var(--valuation-over)";
        } finally {
            this.syncMacroBtn.disabled = false;
            this.syncMacroBtn.innerHTML = `<i data-lucide="refresh-cw"></i> Sync with Live Market`;
            lucide.createIcons();
        }
    }

    async fetchWithTimeout(resource, options = {}) {
        const { timeout = 8000 } = options;
        
        const controller = new AbortController();
        const id = setTimeout(() => controller.abort(), timeout);
        
        try {
            const response = await fetch(resource, {
                ...options,
                signal: controller.signal  
            });
            clearTimeout(id);
            return response;
        } catch (error) {
            clearTimeout(id);
            throw error;
        }
    }

    async fetchTreasuryYield() {
        try {
            const url = `https://api.allorigins.win/get?url=${encodeURIComponent('https://query1.finance.yahoo.com/v8/finance/chart/^TNX?range=1d&interval=1d')}`;
            const res = await this.fetchWithTimeout(url, { timeout: 8000 });
            const data = await res.json();
            const yfData = JSON.parse(data.contents);
            return yfData.chart.result[0].meta.regularMarketPrice;
        } catch (e) {
            console.warn("Failed to fetch Treasury Yield", e);
            return null;
        }
    }

    async fetchDamodaranERP() {
        try {
            const url = `https://api.allorigins.win/get?url=${encodeURIComponent('https://pages.stern.nyu.edu/~adamodar/')}`;
            const res = await this.fetchWithTimeout(url, { timeout: 8000 });
            const data = await res.json();
            const htmlText = data.contents;
            
            const erpMatch = htmlText.match(/Implied Equity Risk Premium\s*(?:\([^\)]+\))?\s*=\s*(\d+\.\d+)%/i) 
                          || htmlText.match(/ERP\s*=\s*(\d+\.\d+)%/i);
            
            if (erpMatch && erpMatch[1]) {
                return parseFloat(erpMatch[1]);
            }
            return 4.60;
        } catch (e) {
            console.warn("Failed to fetch Damodaran ERP", e);
            return null;
        }
    }

    switchTab(tab) {
        if (tab === 'search') {
            this.navSearch.classList.add('active');
            this.navCompare.classList.remove('active');
            this.navPortfolio.classList.remove('active');
            this.sectionSearch.classList.add('active', 'fade-in');
            this.sectionSearch.classList.remove('hidden');
            this.sectionCompare.classList.add('hidden');
            this.sectionCompare.classList.remove('active', 'fade-in');
            this.sectionPortfolio.classList.add('hidden');
            this.sectionDetail.classList.add('hidden');
        } else if (tab === 'compare') {
            this.navCompare.classList.add('active');
            this.navSearch.classList.remove('active');
            this.navPortfolio.classList.remove('active');
            this.sectionCompare.classList.add('active', 'fade-in');
            this.sectionCompare.classList.remove('hidden');
            this.sectionSearch.classList.add('hidden');
            this.sectionSearch.classList.remove('active', 'fade-in');
            this.sectionPortfolio.classList.add('hidden');
            this.sectionDetail.classList.add('hidden');
            
            this.renderCompare();
        } else if (tab === 'portfolio') {
            this.navSearch.classList.remove('active');
            this.navCompare.classList.remove('active');
            this.navPortfolio.classList.add('active');
            this.sectionPortfolio.classList.add('active', 'fade-in');
            this.sectionPortfolio.classList.remove('hidden');
            this.sectionSearch.classList.add('hidden');
            this.sectionCompare.classList.add('hidden');
            this.sectionDetail.classList.add('hidden');

            this.renderPortfolio();
        } else if (tab === 'detail') {
            this.navSearch.classList.remove('active');
            this.navCompare.classList.remove('active');
            this.navPortfolio.classList.remove('active');
            this.sectionDetail.classList.add('active', 'fade-in');
            this.sectionDetail.classList.remove('hidden');
            this.sectionSearch.classList.add('hidden');
            this.sectionCompare.classList.add('hidden');
            this.sectionPortfolio.classList.add('hidden');
        }
    }

    toggleCompare(stockId) {
        if (this.selectedStocks.has(stockId)) {
            this.selectedStocks.delete(stockId);
        } else {
            if (this.selectedStocks.size >= 3) {
                alert('You can compare up to 3 stocks at a time.');
                return;
            }
            this.selectedStocks.add(stockId);
        }
        
        this.updateStickyCompareBar();
        
        this.compareBadge.textContent = this.selectedStocks.size;
        this.renderStocks(); 
        
        if (this.sectionCompare.classList.contains('active')) {
            this.renderCompare();
        }
    }

    updateStickyCompareBar() {
        let bar = document.getElementById('sticky-compare-bar');
        
        if (this.selectedStocks.size === 0) {
            if (bar) bar.remove();
            return;
        }

        if (!bar) {
            bar = document.createElement('div');
            bar.id = 'sticky-compare-bar';
            bar.className = 'sticky-compare-bar fade-in';
            document.body.appendChild(bar);
        }

        bar.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: space-between; max-width: 800px; margin: 0 auto; width: 100%;">
                <div style="display: flex; align-items: center; gap: 15px;">
                    <div style="background: var(--accent-primary); width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 1.1rem; color: white;">
                        ${this.selectedStocks.size}
                    </div>
                    <div style="font-size: 1.1rem; font-weight: 600; color: white;">Stocks selected for comparison</div>
                </div>
                <button id="sticky-compare-btn" class="primary-btn" style="margin: 0; padding: 10px 24px; font-size: 1rem; display: flex; align-items: center; gap: 8px; box-shadow: 0 4px 15px rgba(59, 130, 246, 0.5);">
                    View Comparison <i data-lucide="arrow-right"></i>
                </button>
            </div>
        `;

        document.getElementById('sticky-compare-btn').addEventListener('click', () => {
            this.switchTab('compare');
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
        
        lucide.createIcons();
    }

    formatPrice(price, symbol = '$') {
        if (!price && price !== 0) return 'N/A';
        return `${symbol}${price.toFixed(2)}`;
    }

    calculateValuation(stock) {
        const riskFreeRate = this.riskFreeRate / 100;
        const riskPremium = this.equityRiskPremium / 100;
        const expectedReturn = riskFreeRate + stock.beta * riskPremium;
        const MAX_IMPLIED_PE = 50;
        
        let validModels = [];
        let totalValue = 0;

        // Model 1: Income Approach (GGM or ECM)
        let incomeFairValue = 0;
        let incomeModelName = 'N/A';
        if (stock.dividend > 0 && expectedReturn > stock.growthRate) {
            incomeFairValue = (stock.dividend * (1 + stock.growthRate)) / (expectedReturn - stock.growthRate);
            incomeModelName = 'GGM';
        } else if (stock.eps > 0) {
            const adjustedGrowth = Math.min(stock.growthRate, expectedReturn - 0.02);
            let impliedPE = (adjustedGrowth > 0 && expectedReturn > adjustedGrowth) 
                ? (1 + adjustedGrowth) / (expectedReturn - adjustedGrowth) 
                : 1 / expectedReturn;
            impliedPE = Math.min(impliedPE, MAX_IMPLIED_PE);
            incomeFairValue = stock.eps * impliedPE;
            incomeModelName = 'ECM';
        }
        
        if (incomeFairValue > 0) {
            validModels.push(incomeFairValue);
            totalValue += incomeFairValue;
        }

        // Model 2: Asset/Defensive Approach (Graham Number)
        // Formula: SQRT(22.5 * BookValue * EPS)
        let grahamFairValue = 0;
        if (stock.eps > 0 && stock.bookValue > 0) {
            grahamFairValue = Math.sqrt(22.5 * stock.bookValue * stock.eps);
            validModels.push(grahamFairValue);
            totalValue += grahamFairValue;
        }

        // Model 3: Market/Relative Approach (Peer Multiples)
        // Formula: EPS * Peer Average P/E
        let relativeFairValue = 0;
        if (stock.eps > 0 && stock.peerAveragePE > 0) {
            relativeFairValue = stock.eps * stock.peerAveragePE;
            validModels.push(relativeFairValue);
            totalValue += relativeFairValue;
        }

        let fairPrice = 0;
        if (validModels.length > 0) {
            fairPrice = totalValue / validModels.length;
        }

        // Save detailed results for the modal
        stock.triangulation = {
            incomeModelName: incomeModelName,
            incomeValue: incomeFairValue,
            grahamValue: grahamFairValue,
            relativeValue: relativeFairValue,
            validModelCount: validModels.length
        };

        stock.fairPrice = fairPrice;
        stock.expectedReturn = expectedReturn;
        stock.valuationModel = validModels.length > 0 ? 'Blended (Triangulation)' : 'N/A';

        // 적정가가 0이면 분석 불가 → 'fair'로 분류 (판단 유보)
        if (fairPrice <= 0) {
            stock.valuationStatus = 'fair';
            return;
        }

        const diffRatio = (stock.price - fairPrice) / fairPrice;
        
        if (diffRatio > 0.05) {
            stock.valuationStatus = 'overvalued';
        } else if (diffRatio < -0.05) {
            stock.valuationStatus = 'undervalued';
        } else {
            stock.valuationStatus = 'fair';
        }
    }

    renderStocks() {
        this.stockGrid.innerHTML = '';
        
        let displayStocks = this.stocks;
        if (this.currentFilter !== 'all') {
            displayStocks = this.stocks.filter(s => s.valuationStatus === this.currentFilter);
        }

        if (this.stocks.length === 0) {
            this.stockGrid.innerHTML = `<div class="empty-state" style="grid-column: 1/-1">
                <p>Enter a stock ticker (e.g. TSLA, MSFT) in the search bar and press Enter.</p>
            </div>`;
            return;
        }

        if (displayStocks.length === 0) {
            this.stockGrid.innerHTML = `<div class="empty-state" style="grid-column: 1/-1">
                <p>No stocks match the selected filter.</p>
            </div>`;
            return;
        }

        displayStocks.forEach(stock => {
            const isSelected = this.selectedStocks.has(stock.id);
            const isPositive = stock.change.startsWith('+');
            const changeClass = isPositive ? 'positive' : 'negative';
            const changeIcon = isPositive ? 'trending-up' : 'trending-down';
            
            const badgeLabel = stock.valuationStatus === 'undervalued' ? 'Undervalued' : 
                              (stock.valuationStatus === 'overvalued' ? 'Overvalued' : 'Fair Value');

            const card = document.createElement('div');
            card.className = 'stock-card';
            card.id = `card-${stock.id}`;
            card.innerHTML = `
                <div class="valuation-badge badge-${stock.valuationStatus}">${badgeLabel}</div>
                <div class="card-header">
                    <div>
                        <div class="stock-name">${stock.name}</div>
                        <div class="stock-id">${stock.id}</div>
                    </div>
                    <div class="stock-type">${stock.type}</div>
                </div>
                
                <div class="card-price" id="price-${stock.id}">${this.formatPrice(stock.price)}</div>
                <div class="card-change ${changeClass}">
                    <i data-lucide="${changeIcon}" width="16" height="16"></i>
                    ${stock.change}
                </div>
                
                <div class="card-stats">
                    <div class="stat">
                        <div class="stat-label">Market Cap</div>
                        <div class="stat-value">${stock.marketCap}</div>
                    </div>
                    <div class="stat">
                        <div class="stat-label">PER</div>
                        <div class="stat-value">${stock.per}</div>
                    </div>
                </div>
                
                <div class="card-actions">
                    <button class="compare-btn ${isSelected ? 'selected' : ''}" data-id="${stock.id}" style="display: flex; align-items: center; justify-content: center;">
                        ${isSelected ? '<i data-lucide="check" width="16" height="16" style="margin-right:5px"></i> Added' : '<i data-lucide="plus" width="16" height="16" style="margin-right:5px"></i> Compare'}
                    </button>
                    <button class="analyze-btn" data-analyze-id="${stock.id}">
                        Fair Value
                    </button>
                </div>
                <button class="portfolio-add-btn ${this.portfolio[stock.id] ? 'in-portfolio' : ''}" data-portfolio-id="${stock.id}">
                    <i data-lucide="${this.portfolio[stock.id] ? 'check-circle' : 'briefcase'}" width="16" height="16"></i>
                    ${this.portfolio[stock.id] ? 'In Portfolio' : 'Add to Portfolio'}
                </button>
            `;
            
            const btn = card.querySelector('.compare-btn');
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleCompare(stock.id);
            });

            const analyzeBtn = card.querySelector('.analyze-btn');
            analyzeBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.openCAPMModal(stock.id);
            });

            const portBtn = card.querySelector('.portfolio-add-btn');
            portBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.togglePortfolio(stock.id);
            });

            // Card body click for detailed view
            card.addEventListener('click', () => {
                this.openDetail(stock.id);
            });
            
            this.stockGrid.appendChild(card);
        });
        
        lucide.createIcons();
    }

    // Smart update to avoid full re-render on WebSocket tick
    updatePricesInDOM() {
        this.stocks.forEach(stock => {
            const priceEl = document.getElementById(`price-${stock.id}`);
            if (priceEl && stock.price !== stock.previousPrice) {
                priceEl.textContent = this.formatPrice(stock.price);
                
                // Add flash animation
                priceEl.classList.remove('flash-up', 'flash-down');
                // trigger reflow
                void priceEl.offsetWidth;
                
                if (stock.price > stock.previousPrice) {
                    priceEl.classList.add('flash-up');
                } else if (stock.price < stock.previousPrice) {
                    priceEl.classList.add('flash-down');
                }
            }
        });

        // Also update compare table if active
        if (this.sectionCompare.classList.contains('active')) {
            this.renderCompare();
        }
        if (this.sectionDetail.classList.contains('active')) {
            const currentStockId = this.detailContent.getAttribute('data-stock-id');
            if (currentStockId) {
                const stock = this.stocks.find(s => s.id === currentStockId);
                if (stock) {
                    // Update only price and change in detail view if active
                    const priceEl = this.detailContent.querySelector('.detail-price');
                    const changeEl = this.detailContent.querySelector('.detail-change');
                    if (priceEl) priceEl.textContent = this.formatPrice(stock.price);
                    if (changeEl) {
                        const isPositive = stock.change.startsWith('+');
                        changeEl.className = `detail-change ${isPositive ? 'positive' : 'negative'}`;
                        changeEl.innerHTML = `<i data-lucide="${isPositive ? 'trending-up' : 'trending-down'}" width="20" height="20"></i> ${stock.change}`;
                        lucide.createIcons();
                    }
                }
            }
        }
    }

    openDetail(stockId) {
        const stock = this.stocks.find(s => s.id === stockId);
        if (!stock) return;

        this.switchTab('detail');
        this.detailContent.setAttribute('data-stock-id', stockId);

        const isPositive = stock.change.startsWith('+');
        const changeClass = isPositive ? 'positive' : 'negative';
        const changeIcon = isPositive ? 'trending-up' : 'trending-down';

        this.detailContent.innerHTML = `
            <div class="detail-header">
                <div class="detail-title">
                    <h1>${stock.name}</h1>
                    <div class="ticker">${stock.id} • ${stock.type}</div>
                </div>
                <div class="detail-price-box">
                    <div class="detail-price">${this.formatPrice(stock.price)}</div>
                    <div class="detail-change ${changeClass}">
                        <i data-lucide="${changeIcon}" width="20" height="20"></i>
                        ${stock.change}
                    </div>
                </div>
            </div>

            <div class="chart-wrapper" id="tradingview-container">
                <!-- TradingView Widget will be injected here -->
            </div>

            <div class="detail-grid">
                <div class="detail-card">
                    <h3>Key Statistics</h3>
                    <div class="stats-list">
                        <div class="stat-item">
                            <span class="label">Market Cap</span>
                            <span class="value">${stock.marketCap}</span>
                        </div>
                        <div class="stat-item">
                            <span class="label">PER (TTM)</span>
                            <span class="value">${stock.per}</span>
                        </div>
                        <div class="stat-item">
                            <span class="label">Dividend Yield</span>
                            <span class="value">${stock.dividendYield}</span>
                        </div>
                        <div class="stat-item">
                            <span class="label">Beta</span>
                            <span class="value">${stock.beta.toFixed(2)}</span>
                        </div>
                        <div class="stat-item">
                            <span class="label">EPS</span>
                            <span class="value">${this.formatPrice(stock.eps)}</span>
                        </div>
                        <div class="stat-item">
                            <span class="label">Growth Rate</span>
                            <span class="value">${(stock.growthRate * 100).toFixed(1)}%</span>
                        </div>
                    </div>
                </div>

                <div class="detail-card">
                    <h3>Valuation Triangulation</h3>
                    <div class="capm-result" style="margin-bottom: 20px;">
                        <div class="capm-result-item" style="flex: 1; text-align: center;">
                            <h3 style="font-size: 0.9rem; color: var(--accent-primary); border:none; margin:0; padding:0;">Blended Fair Value</h3>
                            <div class="value" style="font-size: 1.8rem; font-weight: 700; color:white;">${stock.fairPrice > 0 ? this.formatPrice(stock.fairPrice) : 'N/A'}</div>
                        </div>
                    </div>
                    <div style="display: grid; gap: 8px;">
                        <div style="padding:8px; background:rgba(255,255,255,0.05); border-radius:6px; font-size:0.85rem;">
                            <strong>Income Approach:</strong> ${stock.triangulation.incomeValue > 0 ? this.formatPrice(stock.triangulation.incomeValue) : 'N/A'}
                        </div>
                        <div style="padding:8px; background:rgba(255,255,255,0.05); border-radius:6px; font-size:0.85rem;">
                            <strong>Asset Approach:</strong> ${stock.triangulation.grahamValue > 0 ? this.formatPrice(stock.triangulation.grahamValue) : 'N/A'}
                        </div>
                        <div style="padding:8px; background:rgba(255,255,255,0.05); border-radius:6px; font-size:0.85rem;">
                            <strong>Market Approach:</strong> ${stock.triangulation.relativeValue > 0 ? this.formatPrice(stock.triangulation.relativeValue) : 'N/A'}
                        </div>
                    </div>
                </div>
                
                <div class="detail-card" style="grid-column: 1 / -1;">
                    <h3>About ${stock.name}</h3>
                    <p class="description-text">${stock.description}</p>
                </div>
            </div>
        `;

        lucide.createIcons();
        this.renderTradingViewWidget(stock.id);
    }

    renderTradingViewWidget(symbol) {
        // Clean up previous widget
        const container = document.getElementById('tradingview-container');
        container.innerHTML = '';
        
        const script = document.createElement('script');
        script.src = 'https://s3.tradingview.com/tv.js';
        script.async = true;
        script.onload = () => {
            if (typeof TradingView !== 'undefined') {
                new TradingView.widget({
                    "width": "100%",
                    "height": 500,
                    "symbol": symbol,
                    "interval": "D",
                    "timezone": "Etc/UTC",
                    "theme": "dark",
                    "style": "1",
                    "locale": "en",
                    "toolbar_bg": "#f1f3f6",
                    "enable_publishing": false,
                    "hide_sidetoolbar": false,
                    "allow_symbol_change": true,
                    "container_id": "tradingview-container"
                });
            }
        };
        document.head.appendChild(script);
    }

    renderCompare() {
        if (this.selectedStocks.size === 0) {
            this.emptyCompare.classList.remove('hidden');
            this.compareTableWrapper.classList.add('hidden');
            return;
        }

        this.emptyCompare.classList.add('hidden');
        this.compareTableWrapper.classList.remove('hidden');

        const selectedStocksData = Array.from(this.selectedStocks).map(id => 
            this.stocks.find(s => s.id === id)
        );

        this.compareHeader.innerHTML = '<th>Metric</th>';
        selectedStocksData.forEach(stock => {
            this.compareHeader.innerHTML += `
                <th>
                    <div style="font-size:1.2rem; margin-bottom:5px;">${stock.name}</div>
                    <div style="font-size:0.8rem; color:var(--text-secondary); font-weight:normal;">${stock.id}</div>
                </th>
            `;
        });
        
        const rows = [
            { key: 'price', label: 'Current Price', format: (val) => this.formatPrice(val) },
            { key: 'change', label: 'Change', format: (val) => `<span class="${val.startsWith('+') ? 'positive' : 'negative'}">${val}</span>` },
            { key: 'marketCap', label: 'Market Cap' },
            { key: 'per', label: 'PER' },
            { key: 'dividendYield', label: 'Dividend Yield' },
            { key: 'beta', label: 'Beta (Market Sensitivity)', format: (val) => val.toFixed(2) },
            { key: 'eps', label: 'EPS (Earnings Per Share)', format: (val) => this.formatPrice(val) },
            { key: 'description', label: 'Description', format: (val) => `<div style="font-size:0.9rem; line-height:1.4">${val}</div>` }
        ];

        this.compareBody.innerHTML = '';
        
        rows.forEach(row => {
            const tr = document.createElement('tr');
            tr.innerHTML = `<td>${row.label}</td>`;
            
            selectedStocksData.forEach(stock => {
                let val = stock[row.key];
                if (row.format && val !== 'N/A') val = row.format(val, stock);
                tr.innerHTML += `<td class="${row.key === 'price' ? 'live-price-cell' : ''}">${val}</td>`;
            });
            this.compareBody.appendChild(tr);
        });
        
        const removeTr = document.createElement('tr');
        removeTr.innerHTML = `<td></td>`;
        selectedStocksData.forEach(stock => {
            const td = document.createElement('td');
            td.className = 'remove-cell';
            const btn = document.createElement('button');
            btn.className = 'remove-btn';
            btn.innerHTML = '<i data-lucide="x" width="20" height="20"></i>';
            btn.addEventListener('click', () => this.toggleCompare(stock.id));
            td.appendChild(btn);
            removeTr.appendChild(td);
        });
        this.compareBody.appendChild(removeTr);
        
        lucide.createIcons();
    }

    // --- Portfolio Management Methods ---

    togglePortfolio(stockId) {
        if (this.portfolio[stockId]) {
            delete this.portfolio[stockId];
        } else {
            const stock = this.stocks.find(s => s.id === stockId);
            if (!stock) return;
            this.portfolio[stockId] = {
                shares: 10, // Default 10 shares
                costBasis: stock.price
            };
        }
        localStorage.setItem('user_portfolio', JSON.stringify(this.portfolio));
        this.renderStocks();
        if (this.sectionPortfolio.classList.contains('active')) {
            this.renderPortfolio();
        }
    }

    updateShares(stockId, amount) {
        if (this.portfolio[stockId]) {
            this.portfolio[stockId].shares = parseFloat(amount) || 0;
            localStorage.setItem('user_portfolio', JSON.stringify(this.portfolio));
            this.calculatePortfolioMetrics();
        }
    }

    renderPortfolio() {
        let portfolioSymbols = Object.keys(this.portfolio);
        if (portfolioSymbols.length === 0) {
            this.emptyPortfolio.classList.remove('hidden');
            this.portfolioBody.innerHTML = '';
            return;
        }

        this.emptyPortfolio.classList.add('hidden');
        
        // Prepare data for sorting
        const portfolioData = portfolioSymbols.map(symbol => {
            const stock = this.stocks.find(s => s.id === symbol);
            if (!stock) return null;
            const shares = this.portfolio[symbol].shares;
            const marketValue = stock.price * shares;
            return { symbol, stock, shares, marketValue };
        }).filter(Boolean);

        const totalValue = portfolioData.reduce((acc, curr) => acc + curr.marketValue, 0);

        // Apply Sorting
        portfolioData.sort((a, b) => {
            let valA, valB;
            if (this.portfolioSort.key === 'weight' || this.portfolioSort.key === 'marketValue') {
                valA = a.marketValue;
                valB = b.marketValue;
            } else if (this.portfolioSort.key === 'price') {
                valA = a.stock.price;
                valB = b.stock.price;
            } else {
                valA = a.symbol;
                valB = b.symbol;
            }

            if (this.portfolioSort.direction === 'asc') {
                return valA > valB ? 1 : -1;
            } else {
                return valA < valB ? 1 : -1;
            }
        });

        this.portfolioBody.innerHTML = '';

        portfolioData.forEach(item => {
            const { symbol, stock, shares, marketValue } = item;
            const weight = totalValue > 0 ? (marketValue / totalValue) * 100 : 0;

            const row = document.createElement('tr');
            row.innerHTML = `
                <td>
                    <div style="font-weight:600">${stock.id}</div>
                    <div style="font-size:0.8rem; color:var(--text-secondary)">${stock.name}</div>
                </td>
                <td>${this.formatPrice(stock.price)}</td>
                <td>
                    <input type="number" class="shares-input" value="${shares}" data-id="${symbol}">
                </td>
                <td>${this.formatPrice(marketValue)}</td>
                <td>${weight.toFixed(1)}%</td>
                <td>
                    <button class="remove-btn" data-id="${symbol}"><i data-lucide="trash-2" width="18"></i></button>
                </td>
            `;

            row.querySelector('.shares-input').addEventListener('change', (e) => {
                this.updateShares(symbol, e.target.value);
            });

            row.querySelector('.remove-btn').addEventListener('click', () => {
                this.togglePortfolio(symbol);
            });

            this.portfolioBody.appendChild(row);
        });

        lucide.createIcons();
        this.calculatePortfolioMetrics();
    }

    sortPortfolio(key) {
        if (this.portfolioSort.key === key) {
            this.portfolioSort.direction = this.portfolioSort.direction === 'asc' ? 'desc' : 'asc';
        } else {
            this.portfolioSort.key = key;
            this.portfolioSort.direction = 'desc';
        }
        this.renderPortfolio();
    }

    exportPortfolioToCSV() {
        const symbols = Object.keys(this.portfolio);
        if (symbols.length === 0) return alert("No portfolio data to export.");

        let csv = "Ticker,Name,Sector,Price,Shares,Market Value,Weight %,Beta,Fair Value,Upside %\n";
        
        let totalVal = 0;
        const data = symbols.map(s => {
            const stock = this.stocks.find(st => st.id === s);
            if (!stock) return null;
            const mv = stock.price * this.portfolio[s].shares;
            totalVal += mv;
            return { stock, mv };
        }).filter(Boolean);

        data.forEach(item => {
            const weight = (item.mv / totalVal) * 100;
            const upside = item.stock.fairPrice > 0 ? ((item.stock.fairPrice - item.stock.price) / item.stock.price) * 100 : 0;
            
            const row = [
                item.stock.id,
                `"${item.stock.name}"`,
                `"${item.stock.type}"`,
                item.stock.price.toFixed(2),
                this.portfolio[item.stock.id].shares,
                item.mv.toFixed(2),
                weight.toFixed(2),
                item.stock.beta.toFixed(2),
                item.stock.fairPrice.toFixed(2),
                upside.toFixed(2)
            ];
            csv += row.join(",") + "\n";
        });

        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement("a");
        const url = URL.createObjectURL(blob);
        link.setAttribute("href", url);
        link.setAttribute("download", `PharmaScope_Portfolio_${new Date().toISOString().split('T')[0]}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    calculatePortfolioMetrics() {
        const symbols = Object.keys(this.portfolio);
        let totalValue = 0;
        let weightedBeta = 0;
        let weightedUpside = 0;
        let totalWeightForValuation = 0;

        const portfolioData = symbols.map(s => {
            const stock = this.stocks.find(st => st.id === s);
            if (!stock) return null;
            const marketValue = stock.price * this.portfolio[s].shares;
            totalValue += marketValue;
            return { stock, marketValue };
        }).filter(Boolean);

        if (totalValue === 0) {
            this.portfolioTotalValue.textContent = '$0.00';
            this.portfolioWeightedBeta.textContent = '0.00';
            this.portfolioValuationScore.textContent = 'N/A';
            return;
        }

        const sectorWeights = {};

        portfolioData.forEach(item => {
            const weight = item.marketValue / totalValue;
            
            // Update weight cell in UI
            const cell = this.sectionPortfolio.querySelector(`.weight-cell[data-id="${item.stock.id}"]`);
            if (cell) cell.textContent = (weight * 100).toFixed(1) + '%';

            weightedBeta += item.stock.beta * weight;

            if (item.stock.fairPrice > 0) {
                const upside = (item.stock.fairPrice - item.stock.price) / item.stock.price;
                weightedUpside += upside * weight;
                totalWeightForValuation += weight;
            }

            // Sector tracking
            const sector = item.stock.type || 'Other';
            sectorWeights[sector] = (sectorWeights[sector] || 0) + item.marketValue;
        });

        this.portfolioTotalValue.textContent = this.formatPrice(totalValue);
        this.portfolioWeightedBeta.textContent = weightedBeta.toFixed(2);
        
        if (totalWeightForValuation > 0) {
            const finalUpside = (weightedUpside / totalWeightForValuation) * 100;
            const sign = finalUpside > 0 ? '+' : '';
            this.portfolioValuationScore.textContent = `${sign}${finalUpside.toFixed(1)}%`;
            this.portfolioValuationScore.style.color = finalUpside > 5 ? 'var(--valuation-under)' : (finalUpside < -5 ? 'var(--valuation-over)' : 'var(--valuation-fair)');
        }

        this.renderSectorChart(sectorWeights);
    }

    renderSectorChart(sectorWeights) {
        const ctx = document.getElementById('sector-chart').getContext('2d');
        
        if (this.sectorChart) {
            this.sectorChart.destroy();
        }

        const labels = Object.keys(sectorWeights);
        const data = Object.values(sectorWeights);

        this.sectorChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: [
                        '#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#94a3b8', padding: 20 }
                    }
                },
                cutout: '70%'
            }
        });
    }

    openCAPMModal(stockId) {
        const stock = this.stocks.find(s => s.id === stockId);
        if (!stock) return;

        const expectedReturn = stock.expectedReturn;
        const fairPrice = stock.fairPrice;
        const triangulation = stock.triangulation || {};
        
        const isUnderValued = stock.valuationStatus === 'undervalued';
        const diffRatio = stock.price > 0 && fairPrice > 0 ? ((fairPrice - stock.price) / stock.price) * 100 : 0;
        
        let statusText = 'Fair Value';
        if (stock.valuationStatus === 'undervalued') statusText = 'Undervalued';
        if (stock.valuationStatus === 'overvalued') statusText = 'Overvalued';
        const statusClass = stock.valuationStatus;

        // Triangulation Explanations
        let incomeExplanation = '';
        if (triangulation.incomeModelName === 'GGM') {
            incomeExplanation = `📐 <strong>Income (GGM):</strong> $${triangulation.incomeValue.toFixed(2)} <br><span style="font-size:0.8rem; opacity:0.8;">Gordon Growth Model based on Dividends.</span>`;
        } else if (triangulation.incomeModelName === 'ECM') {
            incomeExplanation = `📐 <strong>Income (ECM):</strong> $${triangulation.incomeValue.toFixed(2)} <br><span style="font-size:0.8rem; opacity:0.8;">Earnings Capitalization Model (Capped P/E).</span>`;
        } else {
            incomeExplanation = `⚠️ <strong>Income:</strong> N/A <br><span style="font-size:0.8rem; opacity:0.8;">Negative EPS/Dividend.</span>`;
        }

        let grahamExplanation = '';
        if (triangulation.grahamValue > 0) {
            grahamExplanation = `🏛 <strong>Asset (Graham Number):</strong> $${triangulation.grahamValue.toFixed(2)} <br><span style="font-size:0.8rem; opacity:0.8;">Based on Book Value & EPS. Defensive intrinsic value.</span>`;
        } else {
            grahamExplanation = `⚠️ <strong>Asset (Graham Number):</strong> N/A <br><span style="font-size:0.8rem; opacity:0.8;">Missing Book Value or EPS.</span>`;
        }

        let relativeExplanation = '';
        if (triangulation.relativeValue > 0) {
            relativeExplanation = `📊 <strong>Market (Relative):</strong> $${triangulation.relativeValue.toFixed(2)} <br><span style="font-size:0.8rem; opacity:0.8;">Based on Peer Avg P/E (${stock.peerAveragePE.toFixed(1)}x). Peers: ${stock.peers && stock.peers.length > 0 ? stock.peers.join(', ') : 'Sector Default'}</span>`;
        } else {
            relativeExplanation = `⚠️ <strong>Market (Relative):</strong> N/A <br><span style="font-size:0.8rem; opacity:0.8;">No peer data available.</span>`;
        }

        const maxPrice = Math.max(stock.price, fairPrice) * 1.2;
        const currentPct = maxPrice > 0 ? (stock.price / maxPrice) * 100 : 0;
        const fairPct = maxPrice > 0 ? (fairPrice / maxPrice) * 100 : 0;

        const gaugeColor = stock.valuationStatus === 'undervalued' ? 'var(--success)' : 
                          (stock.valuationStatus === 'overvalued' ? 'var(--danger)' : 'var(--warning)');

        this.capmModalBody.innerHTML = `
            <div style="text-align:center; margin-bottom: 20px;">
                <h3 style="font-size: 1.5rem; color: var(--text-primary);">${stock.name} (${stock.id})</h3>
                <p style="color: var(--text-secondary);">Current Price: <span class="${stock.price > stock.previousPrice ? 'flash-up' : (stock.price < stock.previousPrice ? 'flash-down' : '')}">${this.formatPrice(stock.price)}</span></p>
            </div>
            
            <div class="capm-info-box">
                <div class="capm-formula" style="margin-bottom: 15px; padding-bottom: 15px; border-bottom: 1px solid rgba(255,255,255,0.1);">
                    <strong style="color:var(--accent-primary);">Required Return (CAPM)</strong><br>
                    <span style="font-size:0.8rem; color:var(--text-secondary);">Calculates the discount rate used for the Income Approach.</span><br>
                    <code style="display:inline-block; margin-top:5px; background:rgba(0,0,0,0.3); padding:4px 8px; border-radius:4px;">r = R<sub>f</sub> + β × (R<sub>m</sub> - R<sub>f</sub>) = ${(this.riskFreeRate).toFixed(2)}% + ${stock.beta.toFixed(2)} × ${(this.equityRiskPremium).toFixed(2)}% = <strong>${(expectedReturn * 100).toFixed(2)}%</strong></code>
                </div>

                <div class="capm-result" style="margin-bottom: 15px;">
                    <div class="capm-result-item" style="flex: 1; text-align: center;">
                        <h3 style="font-size: 0.9rem; color: var(--accent-primary);">Blended Fair Value (Triangulation)</h3>
                        <div class="value" style="font-size: 1.8rem; font-weight: 700; margin-top: 5px;">${fairPrice > 0 ? this.formatPrice(fairPrice) : 'N/A'}</div>
                    </div>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr; gap: 10px;">
                    <div style="padding:10px; background:rgba(59,130,246,0.1); border-radius:8px; font-size:0.9rem; line-height:1.4;">
                        ${incomeExplanation}
                    </div>
                    <div style="padding:10px; background:rgba(16,185,129,0.1); border-radius:8px; font-size:0.9rem; line-height:1.4;">
                        ${grahamExplanation}
                    </div>
                    <div style="padding:10px; background:rgba(139,92,246,0.1); border-radius:8px; font-size:0.9rem; line-height:1.4;">
                        ${relativeExplanation}
                    </div>
                </div>
            </div>

            <div class="fair-value-text ${statusClass}">
                ${fairPrice > 0 
                    ? `Based on ${triangulation.validModelCount} valid models, this stock is <strong>${Math.abs(diffRatio).toFixed(1)}%</strong> ${statusText}.`
                    : 'Insufficient financial data for accurate valuation.'}
            </div>

            ${fairPrice > 0 ? `
            <div class="gauge-container">
                <div class="gauge-labels">
                    <span>${this.formatPrice(0)}</span>
                    <span>Fair Value: ${this.formatPrice(fairPrice)}</span>
                    <span>${this.formatPrice(maxPrice)}</span>
                </div>
                <div class="gauge-bar-bg">
                    <div class="gauge-bar-fill" style="width: ${fairPct}%; background: ${gaugeColor};"></div>
                    <div class="gauge-marker" style="left: ${currentPct}%;"></div>
                </div>
            </div>` : ''}
        `;

        this.capmModal.classList.remove('hidden');
        lucide.createIcons();
    }
}

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    new App();
});
