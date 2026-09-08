import { useEffect, useRef } from 'react';
import * as THREE from 'three';

export default function Background3D() {
  const mountRef = useRef(null);

  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    // Scene & Camera
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(
      60,
      window.innerWidth / window.innerHeight,
      0.1,
      1000
    );
    camera.position.z = 180;

    // Renderer
    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    // Particle nodes
    const particleCount = 180;
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);
    const velocities = [];

    const goldColor = new THREE.Color('#d4a843');
    const cyanColor = new THREE.Color('#38bdf8');
    const emeraldColor = new THREE.Color('#34d399');

    for (let i = 0; i < particleCount; i++) {
      const x = (Math.random() - 0.5) * 320;
      const y = (Math.random() - 0.5) * 200;
      const z = (Math.random() - 0.5) * 160;

      positions[i * 3] = x;
      positions[i * 3 + 1] = y;
      positions[i * 3 + 2] = z;

      velocities.push({
        x: (Math.random() - 0.5) * 0.12,
        y: (Math.random() - 0.5) * 0.12,
        z: (Math.random() - 0.5) * 0.08,
      });

      // Palette mix
      const rand = Math.random();
      const col = rand < 0.4 ? goldColor : rand < 0.7 ? cyanColor : emeraldColor;
      colors[i * 3] = col.r;
      colors[i * 3 + 1] = col.g;
      colors[i * 3 + 2] = col.b;
    }

    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    // Particle Texture circle
    const canvas = document.createElement('canvas');
    canvas.width = 32;
    canvas.height = 32;
    const ctx = canvas.getContext('2d');
    const gradient = ctx.createRadialGradient(16, 16, 0, 16, 16, 16);
    gradient.addColorStop(0, 'rgba(255, 255, 255, 1)');
    gradient.addColorStop(0.3, 'rgba(212, 168, 67, 0.8)');
    gradient.addColorStop(1, 'rgba(212, 168, 67, 0)');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, 32, 32);

    const texture = new THREE.CanvasTexture(canvas);

    const material = new THREE.PointsMaterial({
      size: 4.5,
      vertexColors: true,
      map: texture,
      transparent: true,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      opacity: 0.75,
    });

    const particles = new THREE.Points(geometry, material);
    scene.add(particles);

    // Line network connecting nearest neighbors
    const lineGeo = new THREE.BufferGeometry();
    const maxLineConnections = particleCount * 6;
    const linePositions = new Float32Array(maxLineConnections * 3);
    const lineColors = new Float32Array(maxLineConnections * 3);

    lineGeo.setAttribute('position', new THREE.BufferAttribute(linePositions, 3));
    lineGeo.setAttribute('color', new THREE.BufferAttribute(lineColors, 3));

    const lineMat = new THREE.LineSegments(
      lineGeo,
      new THREE.LineBasicMaterial({
        vertexColors: true,
        transparent: true,
        opacity: 0.15,
        blending: THREE.AdditiveBlending,
      })
    );
    scene.add(lineMat);

    // Mouse movement interaction
    let mouseX = 0;
    let mouseY = 0;
    let targetX = 0;
    let targetY = 0;

    const handleMouseMove = (e) => {
      mouseX = (e.clientX - window.innerWidth / 2) * 0.05;
      mouseY = (e.clientY - window.innerHeight / 2) * 0.05;
    };

    window.addEventListener('mousemove', handleMouseMove, { passive: true });

    // Handle Resize
    const handleResize = () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    };
    window.addEventListener('resize', handleResize);

    // Animation Loop
    let animId;
    const posArr = geometry.attributes.position.array;

    const animate = () => {
      animId = requestAnimationFrame(animate);

      // Smooth camera motion
      targetX += (mouseX - targetX) * 0.03;
      targetY += (mouseY - targetY) * 0.03;
      camera.position.x = targetX;
      camera.position.y = -targetY;
      camera.lookAt(0, 0, 0);

      // Rotate whole mesh slowly
      particles.rotation.y += 0.0006;
      particles.rotation.x += 0.0003;
      lineMat.rotation.y = particles.rotation.y;
      lineMat.rotation.x = particles.rotation.x;

      // Update positions
      let lineIndex = 0;
      const connectDist = 42;

      for (let i = 0; i < particleCount; i++) {
        const i3 = i * 3;
        posArr[i3] += velocities[i].x;
        posArr[i3 + 1] += velocities[i].y;
        posArr[i3 + 2] += velocities[i].z;

        // Bounce back within bounds
        if (Math.abs(posArr[i3]) > 160) velocities[i].x *= -1;
        if (Math.abs(posArr[i3 + 1]) > 100) velocities[i].y *= -1;
        if (Math.abs(posArr[i3 + 2]) > 80) velocities[i].z *= -1;

        // Connect nearby points with lines
        for (let j = i + 1; j < particleCount; j++) {
          const j3 = j * 3;
          const dx = posArr[i3] - posArr[j3];
          const dy = posArr[i3 + 1] - posArr[j3 + 1];
          const dz = posArr[i3 + 2] - posArr[j3 + 2];
          const dist = Math.sqrt(dx * dx + dy * dy + dz * dz);

          if (dist < connectDist && lineIndex < maxLineConnections - 6) {
            const alpha = 1 - dist / connectDist;

            linePositions[lineIndex] = posArr[i3];
            linePositions[lineIndex + 1] = posArr[i3 + 1];
            linePositions[lineIndex + 2] = posArr[i3 + 2];

            lineColors[lineIndex] = 0.83 * alpha;
            lineColors[lineIndex + 1] = 0.66 * alpha;
            lineColors[lineIndex + 2] = 0.26 * alpha;

            linePositions[lineIndex + 3] = posArr[j3];
            linePositions[lineIndex + 4] = posArr[j3 + 1];
            linePositions[lineIndex + 5] = posArr[j3 + 2];

            lineColors[lineIndex + 3] = 0.22 * alpha;
            lineColors[lineIndex + 4] = 0.74 * alpha;
            lineColors[lineIndex + 5] = 0.97 * alpha;

            lineIndex += 6;
          }
        }
      }

      geometry.attributes.position.needsUpdate = true;
      lineGeo.setDrawRange(0, lineIndex / 3);
      lineGeo.attributes.position.needsUpdate = true;
      lineGeo.attributes.color.needsUpdate = true;

      renderer.render(scene, camera);
    };

    animate();

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('resize', handleResize);
      if (renderer.domElement.parentNode) {
        renderer.domElement.parentNode.removeChild(renderer.domElement);
      }
      geometry.dispose();
      material.dispose();
      texture.dispose();
      lineGeo.dispose();
      lineMat.material.dispose();
      renderer.dispose();
    };
  }, []);

  return (
    <div
      ref={mountRef}
      style={{
        position: 'fixed',
        inset: 0,
        pointerEvents: 'none',
        zIndex: 0,
        overflow: 'hidden',
      }}
      aria-hidden="true"
    />
  );
}
