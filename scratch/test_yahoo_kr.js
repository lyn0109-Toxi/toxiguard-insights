
async function testYahooKR(ticker) {
    const url = `https://api.allorigins.win/get?url=${encodeURIComponent(`https://query1.finance.yahoo.com/v8/finance/chart/${ticker}?range=1d&interval=1d`)}`;
    const res = await fetch(url);
    const data = await res.json();
    const yfData = JSON.parse(data.contents);
    console.log(`Ticker: ${ticker}`);
    console.log(`Price: ${yfData.chart.result[0].meta.regularMarketPrice}`);
    console.log(`Currency: ${yfData.chart.result[0].meta.currency}`);
}

testYahooKR('005930.KS');
