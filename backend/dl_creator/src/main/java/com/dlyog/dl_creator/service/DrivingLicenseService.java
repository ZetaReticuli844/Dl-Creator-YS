package com.dlyog.dl_creator.service;

import com.dlyog.dl_creator.model.DrivingLicense;
import com.dlyog.dl_creator.record.DrivingLicenseRequest;
import com.dlyog.dl_creator.record.DrivingLicenseResponse;
import com.dlyog.dl_creator.record.DrivingLicenseUpdateRequest;

public interface DrivingLicenseService {
        DrivingLicenseResponse createDrivingLicense(DrivingLicenseRequest drivingLicenseRequest);

        DrivingLicenseResponse getDrivingLicense();
        DrivingLicenseResponse updateStatus(String status);

        DrivingLicenseResponse updateLicenseInfo(DrivingLicenseUpdateRequest drivingLicenseUpdateRequest);

        DrivingLicenseResponse changeAddress(String address);

        DrivingLicenseResponse renewLicense();
}
