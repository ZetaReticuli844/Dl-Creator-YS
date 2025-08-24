package com.dlyog.dl_creator.record;

import java.util.Date;

public record DrivingLicenseUpdateRequest(
        Date issueDate,
        Date expirationDate,
        String firstName,
        String lastName,
        String vehicleType,
        String vehicleMake,
        String address,
        String licenseStatus
) {
}
