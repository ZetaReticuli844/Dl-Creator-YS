import axiosInstance from "../utils/axiosConfig";


export const registerUser = async (userData) => {
  try {
    const response = await axiosInstance.post('/user/createUser', userData);
    return response.data;
  } catch (error) {
    throw error.response.data;
  }
};

export const loginUser = async (credentials) => {
  try {
    const response = await axiosInstance.post('/auth/login', credentials);
    if (response.data.token) {
      // Store token with both keys for compatibility
      localStorage.setItem('token', response.data.token);
      localStorage.setItem('jwt', response.data.token); // For ChatWidget
    }
    return response.data;
  } catch (error) {
    throw error.response.data;
  }
};

export const getCurrentUser = async () => {
  try {
    const response = await axiosInstance.get('/user/currentUser');
    return response.data;
  } catch (error) {
    throw error.response.data;
  }
};

export const logout = () => {
    // Remove all tokens and user data from localStorage
    localStorage.removeItem('token');
    localStorage.removeItem('jwt'); // Remove JWT token too
    localStorage.removeItem('user');
    localStorage.removeItem('userId'); // Remove chat user ID
    
    // Redirect to home page
    window.location.href = '/';
  };