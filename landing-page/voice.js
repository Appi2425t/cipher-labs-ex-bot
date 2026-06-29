const VOICES = {
    welcome: {
        text: "Welcome to Cipher Labs! Your trusted partner for secure and fast crypto exchanges. Whether you're buying or selling, we've got you covered with the best rates and instant processing.",
        rate: 0.95,
        pitch: 1.0
    },
    fast: {
        text: "Lightning fast transactions! No waiting, no delays. Your crypto exchange completes in seconds, not minutes. That's the Cipher Labs promise.",
        rate: 1.1,
        pitch: 1.05
    },
    secure: {
        text: "Security is our DNA. Every transaction is protected with bank-grade encryption. Your funds and data are safe with us. Trade with confidence.",
        rate: 0.9,
        pitch: 0.95
    },
    global: {
        text: "Connect globally, trade locally. We support INR, USD, and USDT exchanges across borders. Break barriers, not rules.",
        rate: 0.95,
        pitch: 1.0
    },
    support: {
        text: "Our support team is available 24 hours a day, 7 days a week. Real humans, real help. Just open a ticket and we'll be there for you.",
        rate: 0.9,
        pitch: 1.0
    },
    exchange: {
        text: "Exchanging crypto has never been easier. Enter your amount, pick your pair, and let our trusted exchangers handle the rest. Simple, safe, and transparent.",
        rate: 0.95,
        pitch: 1.0
    },
    trust: {
        text: "Over a thousand trades completed with zero disputes. Our community of verified exchangers is built on trust. Join us and experience the difference.",
        rate: 0.85,
        pitch: 0.98
    },
    outro: {
        text: "Thank you for choosing Cipher Labs. Visit us on Discord or Telegram. Happy trading, and stay secure!",
        rate: 0.95,
        pitch: 1.02
    }
};

let currentUtterance = null;
const statusEl = document.getElementById('voice-status');

function playVoice(key) {
    if (!('speechSynthesis' in window)) {
        setStatus("Voice not supported in this browser.");
        return;
    }

    window.speechSynthesis.cancel();

    const voice = VOICES[key];
    if (!voice) return;

    const utter = new SpeechSynthesisUtterance(voice.text);
    utter.rate = voice.rate;
    utter.pitch = voice.pitch;

    const voices = window.speechSynthesis.getVoices();
    const english = voices.find(v => v.lang.startsWith('en') && v.name.includes('Google'));
    if (english) utter.voice = english;
    else {
        const fallback = voices.find(v => v.lang.startsWith('en'));
        if (fallback) utter.voice = fallback;
    }

    utter.onstart = () => setStatus("Speaking...");
    utter.onend = () => setStatus("Done.");
    utter.onerror = () => setStatus("Voice error.");

    currentUtterance = utter;
    window.speechSynthesis.speak(utter);
}

function setStatus(msg) {
    if (statusEl) {
        statusEl.textContent = msg;
        statusEl.style.opacity = '1';
        if (msg === "Done.") {
            setTimeout(() => { statusEl.style.opacity = '0.4'; }, 2000);
        }
    }
}

function calcExchange(from) {
    const RATE = 85;
    const inrEl = document.getElementById('inr-input');
    const usdEl = document.getElementById('usd-input');

    if (from === 'inr') {
        const inr = parseFloat(inrEl.value);
        usdEl.value = isNaN(inr) ? '' : (inr / RATE).toFixed(2);
    } else {
        const usd = parseFloat(usdEl.value);
        inrEl.value = isNaN(usd) ? '' : (usd * RATE).toFixed(2);
    }
}

function swapCalc() {
    const inrEl = document.getElementById('inr-input');
    const usdEl = document.getElementById('usd-input');
    const tmp = inrEl.value;
    inrEl.value = usdEl.value;
    usdEl.value = tmp;
    calcExchange('inr');
}

function startExchange() {
    playVoice('exchange');
    document.getElementById('exchange').scrollIntoView({ behavior: 'smooth' });
}

window.speechSynthesis.onvoiceschanged = () => {};
