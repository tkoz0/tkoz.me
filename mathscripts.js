/*
Common JS for math pages
Last updated: 2026-10-24
*/

// Wrap everything to avoid global namespace pollution
(function(){
'use strict';

const MATHJAX_SRC = '/mathjax/tex-svg.js';
const MATHJAX_CLASS = 'mathjax_enable';

// This is for fun
const _msg = new Uint8Array([36, 7, 84, 17, 5, 20, 88, 30, 4, 17, 72, 30, 9, 17,
    30, 77, 84, 13, 7, 0, 17, 1, 65, 7, 7, 7, 4, 12, 5, 8, 26, 15, 74, 12, 25,
    25, 9, 89, 26, 15, 13, 25, 25, 4, 16, 72, 30, 14, 88, 7, 18, 25, 1, 30, 9,
    74, 92, 85, 67, 92, 82, 82, 78, 89, 86, 52, 15, 7, 0, 17, 1, 79, 23, 7, 7,
    65, 25, 3, 5, 84, 1, 4, 2, 20, 24, 5, 17, 72, 30, 9, 29, 77, 7, 29, 26, 25,
    21, 88, 91, 88, 84, 12, 3, 6, 17, 25, 18, 84, 7, 12, 65, 8, 4, 79]);
const _key = new TextEncoder().encode('mathjax');

// For the fun message
function easterEgg1(msg,key) {
    const ret = [];
    for (let i = 0; i < msg.length; ++i)
        ret.push(msg[i] ^ key[i % key.length]);
    return new TextDecoder().decode(new Uint8Array(ret));
}

// Helper for running a function after page has loaded
function onReady(func) {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', func, { once: true });
    } else {
        func();
    }
}

// Create a table of contents as a nested ol/li tag structure
// Uses h2,h3,h4,h5,h6 tags. Reserve h1 for highest level page title.
function makeTableOfContents() {
    const headings = Array.from(document.querySelectorAll('h2,h3,h4,h5,h6'));
    if (headings.length === 0) {
        return null;
    }
    // Lowest number of 2,3,4,5,6
    const topLevel = Math.min(...headings.map(h => Number(h.tagName[1])));
    // Collect ids to avoid a collision, exclude headings so they keep originals
    const usedIds = new Set();
    document.querySelectorAll('[id]').forEach(elem => { usedIds.add(elem.id); });
    headings.forEach(heading => { usedIds.delete(heading.id); });
    let counter = 0;
    // Generate info for the table of contents entries
    const entries = headings.map(heading => {
        let id = heading.id;
        if (!id || usedIds.has(id)) {
            do {
                id = 'toc_' + (++counter);
            } while (usedIds.has(id));
        }
        usedIds.add(id);
        heading.id = id;
        return {
            level: Number(heading.tagName[1]),
            text: heading.textContent,
            id: id
        };
    });
    // Build a nested ordered list structure
    const tocElement = document.createElement('ol');
    let currentLevel = topLevel;
    let currentList = tocElement;
    for (const entry of entries) {
        // Nest lists deeper
        while (currentLevel < entry.level) {
            const nested = document.createElement('ol');
            currentList.appendChild(nested);
            currentList = nested;
            ++currentLevel;
        }
        // Go back up
        while (currentLevel > entry.level) {
            currentList = currentList.parentElement;
            --currentLevel;
        }
        // Create the list item
        const li = document.createElement('li');
        const a = document.createElement('a');
        a.href = '#' + entry.id;
        a.textContent = entry.text;
        li.appendChild(a);
        currentList.appendChild(li);
    }
    return tocElement;
}

// Check if anything on the page is to be rendered with MathJax
function hasMathJaxClass() {
    return document.querySelector('.'+MATHJAX_CLASS) !== null;
}

// Render MathJax in elements with the class
function renderMathJaxElements() {
    if (!window.MathJax || typeof window.MathJax.typesetPromise !== 'function') {
        return;
    }
    // Find top level elements with the MathJax enable class
    const elements = Array.from(document.querySelectorAll('.'+MATHJAX_CLASS))
        .filter(elem => !elem.parentElement?.closest('.'+MATHJAX_CLASS));
    // Render selected elements
    window.MathJax.typesetPromise(elements).catch(err => {
        console.error('MathJax typeset failed:',err);
    });
}

// Setup the MathJax configuration before loading.
function configureMathJax() {
    const cfg = window.MathJax || {};
    const tex = Object.assign({},cfg.tex);
    const options = Object.assign({},cfg.options);
    const startup = Object.assign({},cfg.startup);
    // Use \(...\) and \[...\] for inline and display delimeters.
    tex.inlineMath = [['\\(','\\)']];
    tex.displayMath = [['\\[','\\]']];
    // Error handling for invalid equations (display the message)
    tex.formatError = (jax,err) => {
        console.error('MathJax error:',err);
        return jax.formatError(err);
    };
    startup.typeset = false; // Typeset by class instead of everything
    // Set the options
    window.MathJax = Object.assign({},cfg,{
        tex: tex,
        options: options,
        startup: startup
    });
}

// Load MathJax library for rendering equations
function loadMathJax() {
    if (!hasMathJaxClass()) {
        return; // Skip loading MathJax if it is not needed
    }
    // Ensure the config is ready before loading MathJax
    configureMathJax();
    // Check for guard tag to avoid loading twice
    if (document.getElementById('mathjax_loader')) {
        return;
    }
    // Create the script tag for MathJax
    const tag = document.createElement('script');
    tag.id = 'mathjax_loader';
    tag.async = true;
    tag.src = MATHJAX_SRC;
    tag.addEventListener('error',() => {
        console.error('Failed to load MathJax at ' + MATHJAX_SRC);
    });
    tag.addEventListener('load',() => {
        // Typeset desired parts of the page after MathJax has loaded
        if (window.MathJax.startup && window.MathJax.startup.promise) {
            window.MathJax.startup.promise.then(renderMathJaxElements);
        } else {
            renderMathJaxElements();
        }
    });
    document.head.appendChild(tag);
}

// Things to do after the page loads
onReady(() => {
    loadMathJax();

    // Build the table of contents after the page loads
    const tocElement = document.getElementById('toc');
    if (tocElement) {
        const tocContent = makeTableOfContents();
        if (tocContent) {
            tocElement.replaceChildren(tocContent);
        }
    }

    // Easter egg
    console.log(easterEgg1(_msg,_key));
});

// End of wrapper to avoid global namespace pollution
})();
