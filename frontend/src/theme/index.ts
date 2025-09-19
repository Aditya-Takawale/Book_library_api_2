import { createTheme } from '@mui/material/styles';
import { alpha } from '@mui/material/styles';

declare module '@mui/material/styles' {
  interface Theme {
    gradients: {
      primary: string;
      secondary: string;
      accent: string;
      background: string;
      card: string;
    };
    customShadows: {
      card: string;
      hover: string;
      focus: string;
    };
  }

  interface ThemeOptions {
    gradients?: {
      primary?: string;
      secondary?: string;
      accent?: string;
      background?: string;
      card?: string;
    };
    customShadows?: {
      card?: string;
      hover?: string;
      focus?: string;
    };
  }
}

const baseTheme = createTheme({
  palette: {
    primary: {
      main: '#FF6B35', // Vibrant orange
      light: '#FF8A65',
      dark: '#E65100',
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: '#FF8A50', // Coral
      light: '#FFAB91',
      dark: '#F4511E',
      contrastText: '#FFFFFF',
    },
    background: {
      default: '#FAFAFA',
      paper: '#FFFFFF',
    },
    text: {
      primary: '#2C3E50',
      secondary: '#5D6D7E',
    },
    success: {
      main: '#4CAF50',
      light: '#81C784',
      dark: '#388E3C',
    },
    warning: {
      main: '#FF9800',
      light: '#FFB74D',
      dark: '#F57C00',
    },
    error: {
      main: '#F44336',
      light: '#E57373',
      dark: '#D32F2F',
    },
    info: {
      main: '#2196F3',
      light: '#64B5F6',
      dark: '#1976D2',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 700,
      lineHeight: 1.2,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 600,
      lineHeight: 1.3,
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 600,
      lineHeight: 1.4,
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 500,
      lineHeight: 1.4,
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 500,
      lineHeight: 1.5,
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 500,
      lineHeight: 1.5,
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.6,
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.5,
    },
    button: {
      textTransform: 'none',
      fontWeight: 500,
    },
  },
  shape: {
    borderRadius: 12,
  },
  spacing: 8,
});

const theme = createTheme({
  ...baseTheme,
  gradients: {
    primary: 'linear-gradient(135deg, #FF6B35 0%, #FF8A50 100%)',
    secondary: 'linear-gradient(135deg, #FF8A50 0%, #FFAB91 100%)',
    accent: 'linear-gradient(135deg, #FFE0B2 0%, #FFCC80 100%)',
    background: 'linear-gradient(135deg, #FAFAFA 0%, #F5F5F5 100%)',
    card: 'linear-gradient(135deg, #FFFFFF 0%, #FAFAFA 100%)',
  },
  customShadows: {
    card: '0 8px 32px rgba(255, 107, 53, 0.12)',
    hover: '0 12px 40px rgba(255, 107, 53, 0.2)',
    focus: '0 0 0 3px rgba(255, 107, 53, 0.12)',
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          padding: '12px 24px',
          fontSize: '0.95rem',
          fontWeight: 500,
          textTransform: 'none',
          boxShadow: 'none',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            boxShadow: '0 8px 25px rgba(255, 107, 53, 0.25)',
            transform: 'translateY(-2px)',
          },
        },
        contained: {
          background: 'linear-gradient(135deg, #FF6B35 0%, #FF8A50 100%)',
          color: '#FFFFFF',
          '&:hover': {
            background: 'linear-gradient(135deg, #E65100 0%, #F4511E 100%)',
          },
        },
        outlined: {
          border: '2px solid',
          borderImageSource: 'linear-gradient(135deg, #FF6B35 0%, #FF8A50 100%)',
          borderImageSlice: 1,
          background: 'transparent',
          '&:hover': {
            background: alpha('#FF6B35', 0.08),
          },
        },
        text: {
          '&:hover': {
            background: alpha('#FF6B35', 0.08),
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: '0 8px 32px rgba(255, 107, 53, 0.12)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: '0 12px 40px rgba(255, 107, 53, 0.2)',
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 12,
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            '& fieldset': {
              borderColor: alpha('#FF6B35', 0.23),
            },
            '&:hover fieldset': {
              borderColor: alpha('#FF6B35', 0.5),
            },
            '&.Mui-focused fieldset': {
              borderColor: '#FF6B35',
              borderWidth: 2,
            },
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          fontWeight: 500,
        },
        filled: {
          background: 'linear-gradient(135deg, #FF6B35 0%, #FF8A50 100%)',
          color: '#FFFFFF',
        },
        outlined: {
          borderColor: '#FF6B35',
          color: '#FF6B35',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          background: 'linear-gradient(135deg, #FF6B35 0%, #FF8A50 100%)',
          boxShadow: '0 4px 20px rgba(255, 107, 53, 0.3)',
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          background: 'linear-gradient(180deg, #FFFFFF 0%, #FAFAFA 100%)',
          borderRight: '1px solid rgba(255, 107, 53, 0.12)',
        },
      },
    },
    MuiDialog: {
      styleOverrides: {
        paper: {
          borderRadius: 16,
          background: 'linear-gradient(135deg, #FFFFFF 0%, #FAFAFA 100%)',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
        },
        elevation1: {
          boxShadow: '0 4px 16px rgba(255, 107, 53, 0.08)',
        },
        elevation2: {
          boxShadow: '0 8px 24px rgba(255, 107, 53, 0.12)',
        },
        elevation3: {
          boxShadow: '0 12px 32px rgba(255, 107, 53, 0.16)',
        },
      },
    },
    MuiIconButton: {
      styleOverrides: {
        root: {
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            background: alpha('#FF6B35', 0.08),
            transform: 'scale(1.05)',
          },
        },
      },
    },
    MuiListItem: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          margin: '4px 8px',
          '&.Mui-selected': {
            background: 'linear-gradient(135deg, #FFE0B2 0%, #FFCC80 100%)',
            '&:hover': {
              background: 'linear-gradient(135deg, #FFCC80 0%, #FFB74D 100%)',
            },
          },
          '&:hover': {
            background: alpha('#FF6B35', 0.08),
          },
        },
      },
    },
    MuiTab: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
          '&.Mui-selected': {
            color: '#FF6B35',
          },
        },
      },
    },
    MuiTabs: {
      styleOverrides: {
        indicator: {
          background: 'linear-gradient(135deg, #FF6B35 0%, #FF8A50 100%)',
          height: 3,
          borderRadius: '3px 3px 0 0',
        },
      },
    },
  },
});

export default theme;
