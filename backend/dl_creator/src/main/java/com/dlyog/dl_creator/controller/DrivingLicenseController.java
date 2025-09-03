package com.dlyog.dl_creator.controller;

import com.dlyog.dl_creator.TraceStuff;
import com.dlyog.dl_creator.record.ApiResponse;
import com.dlyog.dl_creator.record.DrivingLicenseRequest;
import com.dlyog.dl_creator.record.DrivingLicenseResponse;
import com.dlyog.dl_creator.record.DrivingLicenseUpdateRequest;
import com.dlyog.dl_creator.service.DrivingLicenseService;
import io.micrometer.core.annotation.Timed;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/drivingLicense")
public class DrivingLicenseController {

    @Autowired
    DrivingLicenseService drivingLicenseService;

    @TraceStuff("createDrivingLicenseController")
    @Timed(value = "controller.createDrivingLicense", description = "Time taken to create driving license")
    @PostMapping("/create")
    public ResponseEntity<?> createDrivingLicense(@RequestBody DrivingLicenseRequest drivingLicenseRequest) {
        DrivingLicenseResponse drivingLicense = drivingLicenseService.createDrivingLicense(drivingLicenseRequest);
        return ResponseEntity.ok(ApiResponse.<DrivingLicenseResponse>builder()
                .success(true)
                .message("Driving license created successfully")
                .data(drivingLicense).build());
    }

    @TraceStuff("getLicenseDetailsController")
    @Timed(value = "controller.getLicenseDetails", description = "Time taken to get driving license details")
    @GetMapping("/getLicenseDetails")
    public ResponseEntity<?> getDrivingLicense() {
        DrivingLicenseResponse drivingLicenseResponse = drivingLicenseService.getDrivingLicense();
        return ResponseEntity.ok(ApiResponse.<DrivingLicenseResponse>builder()
                .success(true)
                .message("Driving license retrieved successfully")
                .data(drivingLicenseResponse).build());
    }

    @TraceStuff("updateStatusController")
    @Timed(value = "controller.updateStatus", description = "Time taken to update driving license status")
    @PostMapping("/updateStatus")
    public ResponseEntity<?> updateStatus(@RequestParam String status) {
        DrivingLicenseResponse drivingLicense = drivingLicenseService.updateStatus(status);
        return ResponseEntity.ok(ApiResponse.<DrivingLicenseResponse>builder()
                .success(true)
                .message("Driving license status updated successfully")
                .data(drivingLicense).build());
    }

    @TraceStuff("updateLicenseInfoController")
    @Timed(value = "controller.updateLicenseInfo", description = "Time taken to update license info")
    @PostMapping("/updateLicenseInfo")
    public ResponseEntity<?> updateLicenseInfo(@RequestBody DrivingLicenseUpdateRequest drivingLicenseRequest) {
        DrivingLicenseResponse drivingLicense = drivingLicenseService.updateLicenseInfo(drivingLicenseRequest);
        return ResponseEntity.ok(ApiResponse.<DrivingLicenseResponse>builder()
                .success(true)
                .message("Driving license info updated successfully")
                .data(drivingLicense).build());
    }

    @TraceStuff("changeAddressController")
    @Timed(value = "controller.changeAddress", description = "Time taken to change address")
    @PostMapping("/changeAddress")
    public ResponseEntity<?> changeAddress(@RequestParam String address) {
        DrivingLicenseResponse drivingLicense = drivingLicenseService.changeAddress(address);
        return ResponseEntity.ok(ApiResponse.<DrivingLicenseResponse>builder()
                .success(true)
                .message("Driving license address changed successfully")
                .data(drivingLicense).build());
    }

    @TraceStuff("renewLicenseController")
    @Timed(value = "controller.renewLicense", description = "Time taken to renew license")
    @PostMapping("/renewLicense")
    public ResponseEntity<?> renewLicense() {
        DrivingLicenseResponse drivingLicense = drivingLicenseService.renewLicense();
        return ResponseEntity.ok(ApiResponse.<DrivingLicenseResponse>builder()
                .success(true)
                .message("Driving license renewed successfully")
                .data(drivingLicense).build());
    }

    @TraceStuff("changeVehicleController")
    @Timed(value = "controller.changeVehicle", description = "Time taken to change vehicle")
    @PostMapping("/changeVehicle")
    public ResponseEntity<?> changeVehicle(@RequestParam String vehicleBrand, @RequestParam String vehicleType) {
        DrivingLicenseResponse drivingLicense = drivingLicenseService.changeVehicle(vehicleBrand, vehicleType);
        return ResponseEntity.ok(ApiResponse.<DrivingLicenseResponse>builder()
                .success(true)
                .message("Driving license vehicle changed successfully")
                .data(drivingLicense).build());
    }
}
