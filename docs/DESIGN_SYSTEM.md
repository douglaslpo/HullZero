# Design System HullZero

## 🎨 Identidade Visual

### Inspiração: Transpetro

O design system do HullZero foi criado inspirado na identidade visual da **Transpetro**, adaptando suas cores institucionais para um sistema moderno de monitoramento de bioincrustação.

### Paleta de Cores

#### Cores Principais

**Azul Transpetro** (`brand.500: #0066CC`)
- Cor principal da marca
- Representa confiança, tecnologia e profissionalismo
- Usado em botões principais, links e elementos de destaque

**Verde Petrobras** (`green.500: #00A859`)
- Cor de sustentabilidade e conformidade
- Representa status positivo, sucesso e conformidade
- Usado em indicadores de status "compliant"

**Amarelo Petrobras** (`yellow.500: #FFC107`)
- Cor de energia e atenção
- Representa alertas, avisos e status "at risk"
- Usado em indicadores de atenção

**Azul Oceano** (`ocean.500: #00BCD4`)
- Cor temática marítima
- Representa o ambiente aquático
- Usado em elementos relacionados à água e navegação

#### Escala de Cores

Cada cor principal possui uma escala de 50 a 900:
- **50-200**: Tons muito claros (backgrounds, hover states)
- **300-400**: Tons médios (bordas, elementos secundários)
- **500**: Cor principal (elementos principais)
- **600-700**: Tons escuros (headers, textos)
- **800-900**: Tons muito escuros (contraste máximo)

### Tipografia

**Fonte Principal**: Inter
- Moderna, legível e profissional
- Excelente para interfaces digitais
- Suporte completo a caracteres latinos

**Hierarquia**:
- **Headings**: Bold (700), tamanhos de xl a 6xl
- **Body**: Regular (400), tamanho base md
- **Labels**: Semibold (600), tamanho sm
- **Mono**: Fira Code (para código e dados técnicos)

### Logo

#### Conceito

A logo do HullZero combina:
1. **Navio estilizado**: Representa a frota marítima
2. **Ondas**: Representam o ambiente aquático
3. **Zero centralizado**: Representa o objetivo de bioincrustação zero
4. **Partículas conectadas**: Representam tecnologia e monitoramento

#### Cores da Logo

- **Gradiente azul-verde** nas ondas (transição suave)
- **Gradiente amarelo-laranja** no navio (energia e movimento)
- **Azul escuro** no zero (foco e precisão)
- **Verde** no centro do zero (sustentabilidade)

#### Versões

1. **Logo Completa**: Símbolo + texto "HullZero" + tagline
2. **Logo Compacta**: Símbolo + texto "HullZero"
3. **Ícone**: Apenas o símbolo (para favicon, app icons)

### Componentes

#### Botões

**Primário** (`colorScheme="brand"`):
- Fundo: `brand.500` (#0066CC)
- Hover: `brand.600` (#003366)
- Texto: Branco

**Secundário** (`variant="outline"`):
- Borda: `brand.500`
- Texto: `brand.500`
- Hover: `brand.50` (fundo claro)

**Ghost** (`variant="ghost"`):
- Sem fundo
- Texto: `brand.600`
- Hover: `brand.50`

#### Cards

- **Background**: Branco
- **Border Radius**: `xl` (0.75rem)
- **Shadow**: `md` (sombra média)
- **Padding**: Padrão do Chakra UI

#### Inputs

- **Border Radius**: `md` (0.375rem)
- **Focus**: Borda `brand.500` + shadow outline
- **Placeholder**: `gray.400`

### Espaçamento

Sistema de espaçamento baseado em múltiplos de 4px:
- `xs`: 0.25rem (4px)
- `sm`: 0.5rem (8px)
- `md`: 1rem (16px)
- `lg`: 1.5rem (24px)
- `xl`: 2rem (32px)
- `2xl`: 3rem (48px)

### Sombras

- **xs**: Muito sutil (bordas)
- **sm**: Sutil (cards pequenos)
- **md**: Média (cards padrão)
- **lg**: Grande (modais)
- **xl**: Muito grande (overlays)
- **outline**: Focus states (azul brand)

### Estados

#### Status Colors

- **Success/Compliant**: `green.500` (#00A859)
- **Warning/At Risk**: `yellow.500` (#FFC107)
- **Error/Non Compliant**: `red.500` (#E53935)
- **Critical**: `red.700` (#C62828)
- **Info**: `brand.500` (#0066CC)

### Responsividade

Breakpoints padrão do Chakra UI:
- **base**: 0px (mobile)
- **sm**: 480px (mobile grande)
- **md**: 768px (tablet)
- **lg**: 992px (desktop)
- **xl**: 1280px (desktop grande)
- **2xl**: 1536px (desktop extra grande)

### Acessibilidade

- **Contraste**: Todas as cores atendem WCAG AA (mínimo 4.5:1)
- **Focus States**: Visíveis e destacados
- **Textos**: Tamanho mínimo de 14px para body
- **Interatividade**: Áreas de toque mínimas de 44x44px

### Uso no Código

```tsx
// Cores
<Box bg="brand.500" color="white" />
<Text color="green.500">Conforme</Text>
<Badge colorScheme="yellow">Atenção</Badge>

// Componentes
<Button colorScheme="brand">Ação Principal</Button>
<Card>Conteúdo</Card>
<Input focusBorderColor="brand.500" />

// Logo
<Logo size="md" showText={true} showTagline={false} />
```

### Recursos

- **Logo SVG**: `/frontend/public/logo.svg`
- **Ícone SVG**: `/frontend/public/logo-icon.svg`
- **Tema**: `/frontend/src/theme.ts`
- **Componente Logo**: `/frontend/src/components/Logo.tsx`

---

**Versão**: 1.0  
**Última atualização**: Novembro 2025  
**Inspiração**: Identidade Visual Transpetro

