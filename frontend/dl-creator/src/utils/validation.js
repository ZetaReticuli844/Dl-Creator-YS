export const validateRegister = (data) => {
    const errors = {};
    
    if (!data.fullName) errors.fullName = 'Full Name is required';
    if (!data.email) errors.email = 'Email is required';
    if (!data.password) errors.password = 'Password is required';
    if (data.password && data.password.length < 6) 
      errors.password = 'Password must be at least 6 characters';
    
    return {
      errors,
      isValid: Object.keys(errors).length === 0
    };
  };
  
  export const validateLicense = (data) => {
    const errors = {};
    
    if (!data.firstName) errors.firstName = 'First Name is required';
    if (!data.lastName) errors.lastName = 'Last Name is required';
    if (!data.vehicleType) errors.vehicleType = 'Vehicle Type is required';
    if (!data.vehicleMake) errors.vehicleMake = 'Vehicle Make is required';
    if (!data.address) errors.address = 'Address is required';
    
    return {
      errors,
      isValid: Object.keys(errors).length === 0
    };
  };

  export const validateLogin = (data) => {
    const errors = {};
    
    if (!data.email) errors.email = 'Email is required';
    if (!data.password) errors.password = 'Password is required';
    
    return {
      errors,
      isValid: Object.keys(errors).length === 0
    };
  };