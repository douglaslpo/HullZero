/**
 * Tema do HullZero - Inspirado na Identidade Visual da Transpetro
 * 
 * Cores baseadas na identidade Transpetro:
 * - Verde Petrobras (Pantone 348C): #00A859
 * - Amarelo Petrobras (Pantone 123C): #FFC107
 * - Azul Institucional: #0066CC
 * 
 * Adaptado para um sistema moderno de monitoramento de bioincrustação
 */

import { extendTheme } from '@chakra-ui/react'

const theme = extendTheme({
  colors: {
    // Paleta principal inspirada na Transpetro
    brand: {
      50: '#E0F2E9',   // Verde muito claro
      100: '#B3E0C6',  // Verde claro
      200: '#80CCA0',  // Verde médio claro
      300: '#4DB87A',  // Verde médio
      400: '#26A85D',  // Verde médio escuro
      500: '#007F3F',  // Verde Transpetro (Philippine Green)
      600: '#006633',  // Verde escuro
      700: '#004C26',  // Verde muito escuro
      800: '#003319',  // Verde quase preto
      900: '#00190D',  // Verde preto
    },
    // Verde sustentabilidade (mantendo consistência com a marca)
    green: {
      50: '#E0F2E9',
      100: '#B3E0C6',
      200: '#80CCA0',
      300: '#4DB87A',
      400: '#26A85D',
      500: '#007F3F',  // Verde Transpetro
      600: '#006633',
      700: '#004C26',
      800: '#003319',
      900: '#00190D',
    },
    // Amarelo energia (inspirado no Amarelo Transpetro/Petrobras)
    yellow: {
      50: '#FFF8E1',
      100: '#FFECB3',
      200: '#FFE082',
      300: '#FFD54F',
      400: '#FFCA28',
      500: '#FFC632',  // Amarelo Transpetro (Sunglow)
      600: '#FFB300',
      700: '#FFA000',
      800: '#FF8F00',
      900: '#FF6F00',
    },
    // Cores semânticas para o sistema
    ocean: {
      50: '#E6F2FF',
      100: '#B3D9FF',
      200: '#80BFFF',
      300: '#4DA6FF',
      400: '#1A8CFF',
      500: '#0066CC',  // Azul original mantido para elementos de água/oceano
      600: '#0052A3',
      700: '#003D7A',
      800: '#002952',
      900: '#001429',
    },
    // Cores de status
    status: {
      success: '#007F3F',    // Verde Transpetro
      warning: '#FFC632',    // Amarelo Transpetro
      error: '#E53935',      // Vermelho
      info: '#0066CC',       // Azul
      compliant: '#007F3F',
      at_risk: '#FFC632',
      non_compliant: '#E53935',
      critical: '#C62828',
    },
  },
  fonts: {
    heading: `'Inter', 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`,
    body: `'Inter', 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`,
    mono: `'Fira Code', 'Courier New', monospace`,
  },
  fontSizes: {
    xs: '0.75rem',
    sm: '0.875rem',
    md: '1rem',
    lg: '1.125rem',
    xl: '1.25rem',
    '2xl': '1.5rem',
    '3xl': '1.875rem',
    '4xl': '2.25rem',
    '5xl': '3rem',
    '6xl': '3.75rem',
  },
  fontWeights: {
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
    extrabold: 800,
  },
  lineHeights: {
    normal: 'normal',
    none: 1,
    shorter: 1.25,
    short: 1.375,
    base: 1.5,
    tall: 1.625,
    taller: 1.75,
  },
  radii: {
    none: '0',
    sm: '0.125rem',
    base: '0.25rem',
    md: '0.375rem',
    lg: '0.5rem',
    xl: '0.75rem',
    '2xl': '1rem',
    '3xl': '1.5rem',
    full: '9999px',
  },
  shadows: {
    xs: '0 0 0 1px rgba(0, 0, 0, 0.05)',
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    base: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
    '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    outline: '0 0 0 3px rgba(0, 102, 204, 0.5)',
    inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
    none: 'none',
  },
  styles: {
    global: {
      body: {
        bg: '#F5F7FA',
        color: '#1A202C',
        fontFamily: 'body',
        lineHeight: 'base',
      },
      '*::placeholder': {
        color: 'gray.400',
      },
      '*, *::before, &::after': {
        borderColor: 'gray.200',
      },
    },
  },
  components: {
    Button: {
      baseStyle: {
        fontWeight: 'semibold',
        borderRadius: 'md',
      },
      sizes: {
        sm: {
          fontSize: 'sm',
          px: 4,
          py: 3,
        },
        md: {
          fontSize: 'md',
          px: 6,
          py: 4,
        },
        lg: {
          fontSize: 'lg',
          px: 8,
          py: 5,
        },
      },
      variants: {
        solid: {
          bg: 'brand.500',
          color: 'white',
          _hover: {
            bg: 'brand.600',
            _disabled: {
              bg: 'brand.300',
            },
          },
        },
        outline: {
          border: '2px solid',
          borderColor: 'brand.500',
          color: 'brand.500',
          _hover: {
            bg: 'brand.50',
          },
        },
        ghost: {
          color: 'brand.600',
          _hover: {
            bg: 'brand.50',
          },
        },
      },
      defaultProps: {
        colorScheme: 'brand',
      },
    },
    Card: {
      baseStyle: {
        container: {
          borderRadius: 'xl',
          boxShadow: 'md',
          bg: 'white',
        },
      },
    },
    Heading: {
      baseStyle: {
        fontWeight: 'bold',
        color: 'gray.800',
      },
    },
    Input: {
      baseStyle: {
        field: {
          borderRadius: 'md',
          _focus: {
            borderColor: 'brand.500',
            boxShadow: '0 0 0 1px var(--chakra-colors-brand-500)',
          },
        },
      },
    },
    Select: {
      baseStyle: {
        field: {
          borderRadius: 'md',
          _focus: {
            borderColor: 'brand.500',
            boxShadow: '0 0 0 1px var(--chakra-colors-brand-500)',
          },
        },
      },
    },
  },
  config: {
    initialColorMode: 'light',
    useSystemColorMode: false,
  },
})

export default theme
