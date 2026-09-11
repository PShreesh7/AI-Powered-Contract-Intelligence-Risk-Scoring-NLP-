import { useState, useRef } from 'react';

export default function Card3D({
  children,
  className = '',
  style = {},
  maxTilt = 8,
  scale = 1.02,
  glare = true,
  onClick,
  ...props
}) {
  const cardRef = useRef(null);
  const [tiltStyle, setTiltStyle] = useState({
    transform: 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)',
    transition: 'transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.4s ease',
  });
  const [glareStyle, setGlareStyle] = useState({
    opacity: 0,
    background: 'none',
  });

  const handleMouseMove = (e) => {
    if (!cardRef.current) return;
    const rect = cardRef.current.getBoundingClientRect();
    const x = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
    const y = Math.max(0, Math.min(1, (e.clientY - rect.top) / rect.height));

    const tiltX = (y - 0.5) * -maxTilt;
    const tiltY = (x - 0.5) * maxTilt;

    setTiltStyle({
      transform: `perspective(1000px) rotateX(${tiltX.toFixed(2)}deg) rotateY(${tiltY.toFixed(2)}deg) scale3d(${scale}, ${scale}, ${scale}) translateZ(10px)`,
      transition: 'transform 0.08s ease-out, box-shadow 0.2s ease',
    });

    if (glare) {
      setGlareStyle({
        opacity: 1,
        background: `radial-gradient(circle at ${x * 100}% ${y * 100}%, rgba(229, 193, 88, 0.15) 0%, rgba(255, 255, 255, 0.08) 35%, rgba(255, 255, 255, 0) 70%)`,
        transition: 'opacity 0.1s ease',
      });
    }
  };

  const handleMouseLeave = () => {
    setTiltStyle({
      transform: 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1) translateZ(0px)',
      transition: 'transform 0.5s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.4s ease',
    });
    setGlareStyle({
      opacity: 0,
      background: 'none',
      transition: 'opacity 0.4s ease',
    });
  };

  return (
    <div
      ref={cardRef}
      className={`card-3d ${className}`}
      style={{
        position: 'relative',
        transformStyle: 'preserve-3d',
        willChange: 'transform',
        ...style,
        ...tiltStyle,
      }}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      onClick={onClick}
      {...props}
    >
      {children}

      {glare && (
        <div
          style={{
            position: 'absolute',
            inset: 0,
            pointerEvents: 'none',
            borderRadius: 'inherit',
            zIndex: 10,
            ...glareStyle,
          }}
          aria-hidden="true"
        />
      )}
    </div>
  );
}
