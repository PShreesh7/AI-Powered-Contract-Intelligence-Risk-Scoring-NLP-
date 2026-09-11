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
      55,
      window.innerWidth / window.innerHeight,
      0.1,
      1000
    );
    camera.position.z = 200;

    // Renderer
    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    // Subtle Particle Field
    const particleCount = 110;
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);
    const velocities = [];

    const goldSoft = new THREE.Color('#c5a059');
    const goldGlint = new THREE.Color('#e2c882');
    const platinumSoft = new THREE.Color('#8fa4bc');

    for (let i = 0; i < particleCount; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 360;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 240;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 160;

      velocities.push({
        x: (Math.random() - 0.5) * 0.04,
        y: (Math.random() - 0.5) * 0.04,
        z: (Math.random() - 0.5) * 0.03,
      });

      const rand = Math.random();
      const col = rand < 0.6 ? goldSoft : rand < 0.85 ? goldGlint : platinumSoft;
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
    gradient.addColorStop(0, 'rgba(255, 255, 255, 0.9)');
    gradient.addColorStop(0.3, 'rgba(197, 160, 89, 0.6)');
    gradient.addColorStop(1, 'rgba(197, 160, 89, 0)');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, 32, 32);

    const texture = new THREE.CanvasTexture(canvas);

    const material = new THREE.PointsMaterial({
      size: 3.5,
      vertexColors: true,
      map: texture,
      transparent: true,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      opacity: 0.55,
    });

    const particles = new THREE.Points(geometry, material);
    scene.add(particles);

    // Elegant, faint background ring
    const ringGeo = new THREE.TorusGeometry(100, 0.35, 16, 120);
    const ringMat = new THREE.MeshBasicMaterial({
      color: 0xc5a059,
      transparent: true,
      opacity: 0.06,
      wireframe: true,
    });
    const ringMesh = new THREE.Mesh(ringGeo, ringMat);
    ringMesh.rotation.x = Math.PI / 3.2;
    ringMesh.position.z = -40;
    scene.add(ringMesh);

    // Second faint orbital ring
    const ring2Geo = new THREE.TorusGeometry(75, 0.25, 12, 100);
    const ring2Mat = new THREE.MeshBasicMaterial({
      color: 0x8fa4bc,
      transparent: true,
      opacity: 0.04,
      wireframe: true,
    });
    const ring2Mesh = new THREE.Mesh(ring2Geo, ring2Mat);
    ring2Mesh.rotation.y = Math.PI / 4;
    ring2Mesh.position.z = -50;
    scene.add(ring2Mesh);

    // Subtle connecting lines (sparse & faint)
    const maxLines = particleCount * 2;
    const linePositions = new Float32Array(maxLines * 6);
    const lineColors = new Float32Array(maxLines * 6);
    const lineGeo = new THREE.BufferGeometry();
    lineGeo.setAttribute('position', new THREE.BufferAttribute(linePositions, 3));
    lineGeo.setAttribute('color', new THREE.BufferAttribute(lineColors, 3));

    const lineMat = new THREE.LineSegments(
      lineGeo,
      new THREE.LineBasicMaterial({
        vertexColors: true,
        transparent: true,
        opacity: 0.07,
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
      mouseX = (e.clientX - window.innerWidth / 2) * 0.02;
      mouseY = (e.clientY - window.innerHeight / 2) * 0.02;
    };

    window.addEventListener('mousemove', handleMouseMove, { passive: true });

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
      targetX += (mouseX - targetX) * 0.02;
      targetY += (mouseY - targetY) * 0.02;
      camera.position.x = targetX;
      camera.position.y = -targetY;
      camera.lookAt(0, 0, 0);

      // Smooth slow rotations
      particles.rotation.y += 0.0003;
      ringMesh.rotation.z += 0.0004;
      ring2Mesh.rotation.x += 0.0003;

      // Update positions
      let lineIndex = 0;
      const connectDist = 34;

      for (let i = 0; i < particleCount; i++) {
        const i3 = i * 3;
        posArr[i3] += velocities[i].x;
        posArr[i3 + 1] += velocities[i].y;
        posArr[i3 + 2] += velocities[i].z;

        if (Math.abs(posArr[i3]) > 170) velocities[i].x *= -1;
        if (Math.abs(posArr[i3 + 1]) > 110) velocities[i].y *= -1;
        if (Math.abs(posArr[i3 + 2]) > 90) velocities[i].z *= -1;

        for (let j = i + 1; j < Math.min(i + 6, particleCount); j++) {
          const j3 = j * 3;
          const dx = posArr[i3] - posArr[j3];
          const dy = posArr[i3 + 1] - posArr[j3 + 1];
          const dz = posArr[i3 + 2] - posArr[j3 + 2];
          const dist = Math.sqrt(dx * dx + dy * dy + dz * dz);

          if (dist < connectDist && lineIndex < maxLines * 6 - 6) {
            const alpha = (1 - dist / connectDist) * 0.45;

            linePositions[lineIndex] = posArr[i3];
            linePositions[lineIndex + 1] = posArr[i3 + 1];
            linePositions[lineIndex + 2] = posArr[i3 + 2];

            lineColors[lineIndex] = 0.77 * alpha;
            lineColors[lineIndex + 1] = 0.63 * alpha;
            lineColors[lineIndex + 2] = 0.35 * alpha;

            linePositions[lineIndex + 3] = posArr[j3];
            linePositions[lineIndex + 4] = posArr[j3 + 1];
            linePositions[lineIndex + 5] = posArr[j3 + 2];

            lineColors[lineIndex + 3] = 0.45 * alpha;
            lineColors[lineIndex + 4] = 0.55 * alpha;
            lineColors[lineIndex + 5] = 0.70 * alpha;

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
      ringGeo.dispose();
      ringMat.dispose();
      ring2Geo.dispose();
      ring2Mat.dispose();
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
