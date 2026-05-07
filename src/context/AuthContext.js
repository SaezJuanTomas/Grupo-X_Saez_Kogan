import { jsx as _jsx } from "react/jsx-runtime";
import { createContext, useState, useContext } from 'react';
const AuthContext = createContext(undefined);
// Mock users database
const MOCK_USERS = {
    admin: {
        password: 'contraseña123',
        user: {
            id: 1,
            username: 'admin',
            role: 'admin',
            company_id: 1,
            active: true
        }
    },
    analyst: {
        password: 'contraseña123',
        user: {
            id: 2,
            username: 'analyst',
            role: 'analyst',
            company_id: 1,
            active: true
        }
    }
};
export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const login = (username, password) => {
        const mockUser = MOCK_USERS[username];
        if (mockUser && mockUser.password === password) {
            setUser(mockUser.user);
            return true;
        }
        return false;
    };
    const logout = () => {
        setUser(null);
    };
    return (_jsx(AuthContext.Provider, { value: {
            user,
            isLoggedIn: user !== null,
            role: user?.role || null,
            login,
            logout
        }, children: children }));
};
export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth debe ser usado dentro de AuthProvider');
    }
    return context;
};
