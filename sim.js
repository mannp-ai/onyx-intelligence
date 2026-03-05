const fs = require('fs');
const jsdom = require("jsdom");
const { JSDOM } = jsdom;
const html = fs.readFileSync('src/static/index.html', 'utf8');
const script = fs.readFileSync('src/static/app.js', 'utf8');
const data = JSON.parse(fs.readFileSync('response_debug.json', 'utf8'));

const dom = new JSDOM(html, { runScripts: "outside-only" });
const window = dom.window;
const document = window.document;

// Mock Chart.js and requestAnimationFrame
window.Chart = function() { return { destroy: () => {} } };
window.requestAnimationFrame = (cb) => { cb(0); };

try {
    // Run script in context
    window.eval(`
        // Need to run the DOMContentLoaded manually
        document.addEventListener = (event, cb) => {
            if (event === 'DOMContentLoaded') {
                window._init = cb;
            }
        };
        ${script}
    `);
    
    // Initialize standard bindings
    window._init();
    
    // Expose showResults so we can trigger it
    const fakeEv = { preventDefault: ()=>{} };
    window.showResults = null;
    
    // Intercept showResults inside the closure by editing app.js slightly
    // Or just run it:
} catch(e) { console.error("INIT ERROR:", e); }

// Edit script to expose showResults to window
const exposeScript = script.replace('function showResults(data) {', 'window.showResults = function showResults(data) {');
try {
    const dom2 = new JSDOM(html, { runScripts: "outside-only" });
    const window2 = dom2.window;
    window2.document.addEventListener = (event, cb) => { if(event === 'DOMContentLoaded') window2._init = cb; };
    window2.Chart = function() { return { destroy: () => {} } };
    window2.requestAnimationFrame = (cb) => { cb(0); };
    window2.eval(exposeScript);
    window2._init();
    window2.showResults(data);
    console.log("SUCCESS!");
} catch(e) {
    console.error("CRASH TRACE:", e.stack);
}
