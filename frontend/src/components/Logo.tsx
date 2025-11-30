/**
 * Componente Logo - HullZero
 * Logo minimalista v2 - H + 0 integrado
 * Versão 2.0 - Minimal
 */

import { HStack, Image } from '@chakra-ui/react'
import { useNavigate } from 'react-router-dom'

interface LogoProps {
  size?: 'sm' | 'md' | 'lg' | 'xl'
  showText?: boolean
  showTagline?: boolean
  onClick?: () => void
}

export default function Logo({
  size = 'md',
  showText = true,
  onClick,
}: LogoProps) {
  const navigate = useNavigate()

  const handleClick = () => {
    if (onClick) {
      onClick()
    } else {
      navigate('/')
    }
  }

  // Tamanhos para diferentes contextos - ajustados para logo compacta
  const sizeMap = {
    sm: { icon: 40, logoHeight: 30, text: 'md', tagline: 'xs' },
    md: { icon: 50, logoHeight: 38, text: 'lg', tagline: 'sm' },
    lg: { icon: 64, logoHeight: 48, text: 'xl', tagline: 'md' },
    xl: { icon: 80, logoHeight: 60, text: '2xl', tagline: 'lg' },
  }

  const dimensions = sizeMap[size]

  // Usar logo v2 minimal por padrão
  const logoPath = "/logo-v2-minimal.svg"
  const iconPath = "/logo-icon-v2-minimal.svg"

  return (
    <HStack
      spacing={3}
      cursor={onClick ? 'pointer' : 'default'}
      onClick={handleClick}
      _hover={onClick ? { opacity: 0.85 } : {}}
      transition="opacity 0.2s"
      align="center"
    >
      {showText ? (
        // Logo completa (horizontal) - SVG externo
        <Image
          src={logoPath}
          alt="HullZero Logo"
          height={dimensions.logoHeight}
          maxW="100%"
          objectFit="contain"
          loading="eager"
        />
      ) : (
        // Apenas ícone - SVG externo
        <Image
          src={iconPath}
          alt="HullZero Icon"
          boxSize={dimensions.icon}
          objectFit="contain"
          loading="eager"
        />
      )}
    </HStack>
  )
}
