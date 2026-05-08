
const API_KEY = 'd7oo6ghr01qsb7bfl340d7oo6ghr01qsb7bfl34g';

async function testSearch(query) {
    const res = await fetch(`https://finnhub.io/api/v1/search?q=${encodeURIComponent(query)}&token=${API_KEY}`);
    const data = await res.json();
    console.log(`Query: ${query}`);
    console.log(JSON.stringify(data.result.slice(0, 3), null, 2));
}

testSearch('Pfizer');
testSearch('Samsung');
