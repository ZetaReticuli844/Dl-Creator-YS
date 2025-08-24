import axiosInstance from '../utils/axiosConfig';

export const createDrivingLicense = async (licenseData) => {
  try {
    const response = await axiosInstance.post('/drivingLicense/create', licenseData);
    return response.data;
  } catch (error) {
    throw error.response.data;
  }
};

export const getLicenseDetails = async () => {
  try {
    const response = await axiosInstance.get('/drivingLicense/getLicenseDetails');
    return response.data;
  } catch (error) {
    throw error.response.data;
  }
};