/**
 * Componente BrandHeader - Header com logo e navegação
 * Melhorado com design inspirado na Transpetro
 * Menu otimizado para melhor visual e posicionamento
 */

import { Box, Container, HStack, Button, Menu, MenuButton, MenuList, MenuItem, Avatar, Text, useBreakpointValue, Flex } from '@chakra-ui/react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { ChevronDownIcon, HamburgerIcon } from '@chakra-ui/icons'
import { useAuth } from '../contexts/AuthContext'
import Logo from './Logo'
import { useState } from 'react'

export default function BrandHeader() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  // Detectar breakpoints
  const isMobile = useBreakpointValue({ base: true, lg: false })
  const showFullMenu = useBreakpointValue({ base: false, md: true })

  const menuItems = [
    { path: '/', label: 'Dashboard' },
    { path: '/fleet', label: 'Frota' },
    { path: '/compliance', label: 'Conformidade' },
    { path: '/operational-data', label: 'Dados Operacionais' },
    { path: '/maintenance', label: 'Manutenção' },
    { path: '/invasive-species', label: 'Espécies Invasoras' },
  ]

  if (user) {
    menuItems.push({ path: '/users', label: 'Usuários' })
  }

  const isActive = (path: string) => location.pathname === path

  return (
    <Box 
      bg="brand.600" 
      color="white" 
      py={3}
      boxShadow="lg"
      borderBottom="3px solid"
      borderColor="brand.500"
      position="sticky"
      top={0}
      zIndex={1000}
    >
      <Container maxW="container.xl">
        <Flex 
          justify="space-between" 
          align="center" 
          gap={6}
          flexWrap="nowrap"
        >
          {/* Logo */}
          <Box flexShrink={0}>
            <Logo size="sm" showText={true} showTagline={false} />
          </Box>
          
          {/* Menu Desktop - Uma linha, bem espaçado */}
          {showFullMenu && (
            <HStack 
              spacing={1}
              flex={1}
              justify="center"
              align="center"
              overflowX="auto"
              px={2}
              css={{
                '&::-webkit-scrollbar': {
                  height: '3px',
                },
                '&::-webkit-scrollbar-track': {
                  background: 'rgba(255, 255, 255, 0.1)',
                },
                '&::-webkit-scrollbar-thumb': {
                  background: 'rgba(255, 255, 255, 0.3)',
                  borderRadius: '2px',
                },
              }}
            >
              {menuItems.map((item) => (
                <Button
                  key={item.path}
                  as={Link}
                  to={item.path}
                  variant="ghost"
                  colorScheme="whiteAlpha"
                  size="md"
                  px={4}
                  py={2}
                  fontSize="sm"
                  fontWeight={isActive(item.path) ? 'bold' : 'medium'}
                  bg={isActive(item.path) ? 'whiteAlpha.200' : 'transparent'}
                  color={isActive(item.path) ? 'white' : 'whiteAlpha.900'}
                  borderBottom={isActive(item.path) ? '3px solid' : '3px solid transparent'}
                  borderColor={isActive(item.path) ? 'white' : 'transparent'}
                  borderRadius="none"
                  _hover={{
                    bg: 'whiteAlpha.150',
                    color: 'white',
                    borderBottom: '3px solid',
                    borderColor: 'whiteAlpha.500',
                  }}
                  _active={{
                    bg: 'whiteAlpha.250',
                  }}
                  transition="all 0.2s"
                  whiteSpace="nowrap"
                  minH="44px"
                  flexShrink={0}
                >
                  {item.label}
                </Button>
              ))}
            </HStack>
          )}

          {/* Menu Mobile - Dropdown */}
          {!showFullMenu && (
            <Menu isOpen={isMenuOpen} onOpen={() => setIsMenuOpen(true)} onClose={() => setIsMenuOpen(false)}>
              <MenuButton
                as={Button}
                variant="ghost"
                colorScheme="whiteAlpha"
                size="md"
                px={3}
              >
                <HamburgerIcon boxSize={6} />
              </MenuButton>
              <MenuList color="gray.800" minW="220px">
                {menuItems.map((item) => (
                  <MenuItem
                    key={item.path}
                    as={Link}
                    to={item.path}
                    onClick={() => setIsMenuOpen(false)}
                    bg={isActive(item.path) ? 'brand.50' : 'transparent'}
                    fontWeight={isActive(item.path) ? 'bold' : 'normal'}
                    color={isActive(item.path) ? 'brand.600' : 'gray.700'}
                  >
                    {item.label}
                  </MenuItem>
                ))}
              </MenuList>
            </Menu>
          )}

          {/* Menu do Usuário */}
          {user && (
            <Menu>
              <MenuButton 
                as={Button} 
                rightIcon={<ChevronDownIcon />} 
                variant="ghost" 
                colorScheme="whiteAlpha"
                size="md"
                px={3}
                flexShrink={0}
              >
                <HStack spacing={2}>
                  <Avatar size="sm" name={user.full_name} bg="brand.500" />
                  {!isMobile && (
                    <Text fontSize="sm" fontWeight="medium">
                      {user.full_name.split(' ')[0]}
                    </Text>
                  )}
                </HStack>
              </MenuButton>
              <MenuList color="gray.800" minW="250px">
                <MenuItem>
                  <Box>
                    <Text fontSize="sm" fontWeight="bold" color="gray.800">
                      {user.full_name}
                    </Text>
                    <Text fontSize="xs" color="gray.600">
                      {user.email}
                    </Text>
                  </Box>
                </MenuItem>
                <MenuItem>
                  <Text fontSize="sm" color="gray.600">
                    Papéis: {user.roles?.join(', ') || 'Nenhum'}
                  </Text>
                </MenuItem>
                <MenuItem onClick={handleLogout} color="red.500" fontWeight="medium">
                  Sair
                </MenuItem>
              </MenuList>
            </Menu>
          )}
        </Flex>
      </Container>
    </Box>
  )
}
