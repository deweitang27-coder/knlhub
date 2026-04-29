import { useMemo } from 'react'

function BackgroundParticles() {
  const particles = useMemo(() => {
    return Array.from({ length: 20 }, (_, i) => ({
      id: i,
      left: `${Math.random() * 100}%`,
      size: Math.random() * 4 + 2,
      delay: Math.random() * 10,
      duration: Math.random() * 10 + 10,
      opacity: Math.random() * 0.3 + 0.1,
    }))
  }, [])

  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
      {particles.map((particle) => (
        <div
          key={particle.id}
          className="absolute rounded-full bg-primary-400"
          style={{
            left: particle.left,
            bottom: '-10px',
            width: `${particle.size}px`,
            height: `${particle.size}px`,
            opacity: particle.opacity,
            animation: `drift ${particle.duration}s linear infinite`,
            animationDelay: `${particle.delay}s`,
            filter: `blur(${particle.size / 2}px)`,
          }}
        />
      ))}
    </div>
  )
}

export default BackgroundParticles
