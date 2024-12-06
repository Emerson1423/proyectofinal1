const alphabet = 'ABCDEFGHIJKLMNÑOPQRSTUVWXYZ'.split('');
alphabet.splice(alphabet.indexOf('H') + 1, 0, 'CH');
let currentIndex = 0;

const letterDisplay = document.getElementById('letterDisplay');
const signImage = document.getElementById('signImage');
const prevButton = document.getElementById('prevButton');
const nextButton = document.getElementById('nextButton');
const alphabetGrid = document.getElementById('alphabetGrid');

function updateDisplay() {
    const currentLetter = alphabet[currentIndex];
    letterDisplay.textContent = currentLetter;

    // Define las rutas usando basePath
    const gifPath = `${basePath}${currentLetter}.gif`;
    const jpegPath = `${basePath}${currentLetter}.jpeg`;

    // Verificar si el GIF existe
    const tempImage = new Image();
    tempImage.onload = function() {
        signImage.src = gifPath;
        signImage.alt = `Seña para la letra ${currentLetter}`;
    };
    tempImage.onerror = function() {
        signImage.src = jpegPath;
        signImage.alt = `Seña para la letra ${currentLetter}`;
    };
    tempImage.src = gifPath;

    // Actualizar botones y el grid
    prevButton.disabled = currentIndex === 0;
    nextButton.disabled = currentIndex === alphabet.length - 1;

    document.querySelectorAll('.letter-button').forEach((button, index) => {
        button.classList.toggle('active', index === currentIndex);
    });
}

function navigate(direction) {
    currentIndex = Math.max(0, Math.min(alphabet.length - 1, currentIndex + direction));
    updateDisplay();
}

prevButton.addEventListener('click', () => navigate(-1));
nextButton.addEventListener('click', () => navigate(1));

alphabet.forEach((letter, index) => {
    const button = document.createElement('button');
    button.className = 'letter-button';
    button.textContent = letter;
    button.setAttribute('aria-label', `Ver seña para la letra ${letter}`);
    button.addEventListener('click', () => {
        currentIndex = index;
        updateDisplay();
    });
    alphabetGrid.appendChild(button);
});

updateDisplay();
