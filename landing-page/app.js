const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('bg'), antialias: true, alpha: true });

renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setClearColor(0x0a0a0f, 1);

const ambientLight = new THREE.AmbientLight(0x404040, 0.5);
scene.add(ambientLight);

const pointLight1 = new THREE.PointLight(0x2ecc71, 2, 50);
pointLight1.position.set(10, 10, 10);
scene.add(pointLight1);

const pointLight2 = new THREE.PointLight(0x3498db, 2, 50);
pointLight2.position.set(-10, -10, 5);
scene.add(pointLight2);

const torusGeometry = new THREE.TorusKnotGeometry(3, 0.8, 200, 32);
const torusMaterial = new THREE.MeshStandardMaterial({
    color: 0x2ecc71,
    wireframe: true,
    transparent: true,
    opacity: 0.3,
    emissive: 0x1a5c3a,
    emissiveIntensity: 0.2
});
const torus = new THREE.Mesh(torusGeometry, torusMaterial);
scene.add(torus);

const particlesGeometry = new THREE.BufferGeometry();
const particleCount = 1500;
const posArray = new Float32Array(particleCount * 3);
const colorsArray = new Float32Array(particleCount * 3);

for (let i = 0; i < particleCount; i++) {
    posArray[i * 3] = (Math.random() - 0.5) * 40;
    posArray[i * 3 + 1] = (Math.random() - 0.5) * 40;
    posArray[i * 3 + 2] = (Math.random() - 0.5) * 40;

    const color = new THREE.Color();
    color.setHSL(0.35 + Math.random() * 0.15, 0.8, 0.5 + Math.random() * 0.3);
    colorsArray[i * 3] = color.r;
    colorsArray[i * 3 + 1] = color.g;
    colorsArray[i * 3 + 2] = color.b;
}

particlesGeometry.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
particlesGeometry.setAttribute('color', new THREE.BufferAttribute(colorsArray, 3));

const particlesMaterial = new THREE.PointsMaterial({
    size: 0.06,
    vertexColors: true,
    transparent: true,
    opacity: 0.8,
    blending: THREE.AdditiveBlending
});
const particles = new THREE.Points(particlesGeometry, particlesMaterial);
scene.add(particles);

const ringGeometry = new THREE.RingGeometry(5, 5.1, 64);
const ringMaterial = new THREE.MeshBasicMaterial({ color: 0x3498db, transparent: true, opacity: 0.15, side: THREE.DoubleSide });
const ring1 = new THREE.Mesh(ringGeometry, ringMaterial);
ring1.rotation.x = Math.PI / 2;
scene.add(ring1);

const ring2 = new THREE.Mesh(
    new THREE.RingGeometry(7, 7.05, 64),
    new THREE.MeshBasicMaterial({ color: 0x2ecc71, transparent: true, opacity: 0.1, side: THREE.DoubleSide })
);
ring2.rotation.x = Math.PI / 3;
ring2.rotation.y = Math.PI / 4;
scene.add(ring2);

camera.position.z = 12;

let mouseX = 0;
let mouseY = 0;
let targetX = 0;
let targetY = 0;

document.addEventListener('mousemove', (e) => {
    mouseX = (e.clientX / window.innerWidth) * 2 - 1;
    mouseY = -(e.clientY / window.innerHeight) * 2 + 1;
});

function animate() {
    requestAnimationFrame(animate);

    targetX += (mouseX * 0.5 - targetX) * 0.05;
    targetY += (mouseY * 0.5 - targetY) * 0.05;

    torus.rotation.x += 0.003;
    torus.rotation.y += 0.005;
    torus.rotation.x += targetY * 0.01;
    torus.rotation.y += targetX * 0.01;

    particles.rotation.y += 0.0005;
    particles.rotation.x += 0.0002;

    ring1.rotation.z += 0.001;
    ring2.rotation.z -= 0.0008;

    pointLight1.position.x = Math.sin(Date.now() * 0.001) * 10;
    pointLight1.position.z = Math.cos(Date.now() * 0.001) * 10;

    camera.position.x += (targetX * 2 - camera.position.x) * 0.02;
    camera.position.y += (targetY * 2 - camera.position.y) * 0.02;
    camera.lookAt(scene.position);

    renderer.render(scene, camera);
}

animate();

window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});

gsap.registerPlugin(ScrollTrigger);

gsap.from('.hero-title .line', {
    y: 80,
    opacity: 0,
    duration: 1,
    stagger: 0.15,
    ease: 'power3.out'
});

gsap.from('.hero-sub', {
    y: 40,
    opacity: 0,
    duration: 1,
    delay: 0.6,
    ease: 'power3.out'
});

gsap.from('.hero-btns', {
    y: 30,
    opacity: 0,
    duration: 1,
    delay: 0.8,
    ease: 'power3.out'
});

gsap.utils.toArray('.feature-card').forEach((card, i) => {
    gsap.from(card, {
        scrollTrigger: {
            trigger: card,
            start: 'top 85%',
            toggleActions: 'play none none none'
        },
        y: 60,
        opacity: 0,
        duration: 0.8,
        delay: i * 0.1,
        ease: 'power3.out'
    });
});

gsap.from('.exchange-panel', {
    scrollTrigger: {
        trigger: '.exchange-panel',
        start: 'top 80%'
    },
    y: 80,
    opacity: 0,
    duration: 1,
    ease: 'power3.out'
});

gsap.from('.voice-panel', {
    scrollTrigger: {
        trigger: '.voice-panel',
        start: 'top 80%'
    },
    y: 80,
    opacity: 0,
    duration: 1,
    ease: 'power3.out'
});
