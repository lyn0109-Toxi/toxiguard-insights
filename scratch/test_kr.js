
const API_KEY = 'd7oo6ghr01qsb7bfl340d7oo6ghr01qsb7bfl34g';

async function testKRStock(ticker) {
    const [profileRes, quoteRes, metricRes] = await Promise.all([
        fetch(`https://finnhub.io/api/v1/stock/profile2?symbol=${ticker}&token=${API_KEY}`),
        fetch(`https://finnhub.io/api/v1/quote?symbol=${ticker}&token=${API_KEY}`),
        fetch(`https://finnhub.io/api/v1/stock/metric?symbol=${ticker}&metric=all&token=${API_KEY}`)
    ]);

    const profile = await profileRes.json();
    const quote = await quoteRes.json();
    const metrics = await metricRes.json();

    console.log(`Ticker: ${ticker}`);
    console.log(`Name: ${profile.name}, Currency: ${profile.currency}`);
    console.log(`Price: ${quote.c}`);
    console.log(`PE: ${metrics.metric?.peAnnual}`);
}

testKRStock('005930.KS');
