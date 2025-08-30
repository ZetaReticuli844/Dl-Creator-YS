package com.dlyog.dl_creator.service;

import com.dlyog.dl_creator.Enum.LicenseStatusEnum;
import com.dlyog.dl_creator.TraceStuff;
import com.dlyog.dl_creator.model.DrivingLicense;
import com.dlyog.dl_creator.model.User;
import com.dlyog.dl_creator.record.DrivingLicenseRequest;
import com.dlyog.dl_creator.record.DrivingLicenseResponse;
import com.dlyog.dl_creator.record.DrivingLicenseUpdateRequest;
import com.dlyog.dl_creator.repository.DrivingLicenseJpa;
import io.opentelemetry.api.GlobalOpenTelemetry;
import io.opentelemetry.api.trace.Span;
import io.opentelemetry.api.trace.Tracer;
import io.opentelemetry.context.Scope;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;

import java.util.Date;
import java.util.Random;

@Service
public class DrivingLicenseServiceImpl implements DrivingLicenseService {
    @Autowired
    DrivingLicenseJpa drivingLicenseJpa;


    @TraceStuff("createDrivingLicenseService")
    @Override
    public DrivingLicenseResponse createDrivingLicense(DrivingLicenseRequest drivingLicenseRequest) {
        try {
            Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
            User currentUser = (User) authentication.getPrincipal();
            DrivingLicense drivingLicense = new DrivingLicense();
            drivingLicense.setUser(currentUser);
            drivingLicense.setFirstName(drivingLicenseRequest.firstName());
            drivingLicense.setLastName(drivingLicenseRequest.lastName());
            drivingLicense.setLicenseNumber(generateLicenseNumber(currentUser.getId()));
            drivingLicense.setIssueDate(new java.util.Date());
            drivingLicense.setExpirationDate(new java.util.Date());
            drivingLicense.setVehicleType(drivingLicenseRequest.vehicleType());
            drivingLicense.setVehicleMake(drivingLicenseRequest.vehicleMake());
            drivingLicense.setAddress(drivingLicenseRequest.address());
            drivingLicense.setLicenseStatus(LicenseStatusEnum.PENDING);
            drivingLicenseJpa.save(drivingLicense);
            return DrivingLicenseResponse.builder()
                    .id(drivingLicense.getId())
                    .userId(currentUser.getId())
                    .licenseNumber(drivingLicense.getLicenseNumber())
                    .issueDate(drivingLicense.getIssueDate())
                    .expirationDate(drivingLicense.getExpirationDate())
                    .firstName(drivingLicense.getFirstName())
                    .lastName(drivingLicense.getLastName())
                    .vehicleType(drivingLicense.getVehicleType())
                    .vehicleMake(drivingLicense.getVehicleMake())
                    .licenseStatus(drivingLicense.getLicenseStatus().toString())
                    .address(drivingLicense.getAddress())
                    .build();
        } catch (Exception e) {
            System.out.println("WRONG " + e.getMessage());
            return null;
        }

    }

    @TraceStuff("getDrivingLicenseService")
    @Override
    public DrivingLicenseResponse getDrivingLicense() {
        try {
            Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
            User currentUser = (User) authentication.getPrincipal();
            DrivingLicense drivingLicense = drivingLicenseJpa.findByUserId(currentUser.getId());
            DrivingLicenseResponse drivingLicenseResponse = DrivingLicenseResponse.builder()
                    .id(drivingLicense.getId())
                    .userId(currentUser.getId())
                    .licenseNumber(drivingLicense.getLicenseNumber())
                    .issueDate(drivingLicense.getIssueDate())
                    .expirationDate(drivingLicense.getExpirationDate())
                    .firstName(drivingLicense.getFirstName())
                    .lastName(drivingLicense.getLastName())
                    .vehicleType(drivingLicense.getVehicleType())
                    .vehicleMake(drivingLicense.getVehicleMake())
                    .address(drivingLicense.getAddress())
                    .build();
            return drivingLicenseResponse;
        } catch (Exception e) {
            return null;
        }
    }

    @TraceStuff("updateStatusService")
    @Override
    public DrivingLicenseResponse updateStatus(String status) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        User currentUser = (User) authentication.getPrincipal();
        DrivingLicense drivingLicense = drivingLicenseJpa.findByUserId(currentUser.getId());
        if (status.equals("PENDING")) {
            drivingLicense.setLicenseStatus(LicenseStatusEnum.PENDING);
        } else if (status.equals("CANCELLED")) {
            drivingLicense.setLicenseStatus(LicenseStatusEnum.CANCELLED);
        } else if (status.equals("SUBMITTED")) {
            drivingLicense.setLicenseStatus(LicenseStatusEnum.SUBMITTED);
        } else if (status.equals("PRINTED")) {
            drivingLicense.setLicenseStatus(LicenseStatusEnum.PRINTED);
        } else if (status.equals("DISPATCHED")) {
            drivingLicense.setLicenseStatus(LicenseStatusEnum.DISPATCHED);
        } else if (status.equals("DELIVERED")) {
            drivingLicense.setLicenseStatus(LicenseStatusEnum.DELIVERED);
        }
        drivingLicenseJpa.save(drivingLicense);
        DrivingLicenseResponse drivingLicenseResponse = DrivingLicenseResponse.builder()
                .id(drivingLicense.getId())
                .userId(currentUser.getId())
                .licenseNumber(drivingLicense.getLicenseNumber())
                .issueDate(drivingLicense.getIssueDate())
                .expirationDate(drivingLicense.getExpirationDate())
                .firstName(drivingLicense.getFirstName())
                .lastName(drivingLicense.getLastName())
                .vehicleType(drivingLicense.getVehicleType())
                .vehicleMake(drivingLicense.getVehicleMake())
                .licenseStatus(drivingLicense.getLicenseStatus().toString())
                .address(drivingLicense.getAddress())
                .build();
        return drivingLicenseResponse;

    }

    @TraceStuff("updateLicenseInfoService")
    @Override
    public DrivingLicenseResponse updateLicenseInfo(DrivingLicenseUpdateRequest drivingLicenseUpdateRequest) {
        User currentUser = (User) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
        DrivingLicense drivingLicense = drivingLicenseJpa.findByUserId(currentUser.getId());
        drivingLicense.setFirstName(drivingLicenseUpdateRequest.firstName());
        drivingLicense.setLastName(drivingLicenseUpdateRequest.lastName());
        drivingLicense.setVehicleType(drivingLicenseUpdateRequest.vehicleType());
        drivingLicense.setVehicleMake(drivingLicenseUpdateRequest.vehicleMake());
        String status = drivingLicenseUpdateRequest.licenseStatus();
        if (status.equals("PENDING")) {
            drivingLicense.setLicenseStatus(LicenseStatusEnum.PENDING);
        } else if (status.equals("CANCELLED")) {
            drivingLicense.setLicenseStatus(LicenseStatusEnum.CANCELLED);
        } else if (status.equals("SUBMITTED")) {
            drivingLicense.setLicenseStatus(LicenseStatusEnum.SUBMITTED);
        } else if (status.equals("PRINTED")) {
            drivingLicense.setLicenseStatus(LicenseStatusEnum.PRINTED);
        } else if (status.equals("DISPATCHED")) {
            drivingLicense.setLicenseStatus(LicenseStatusEnum.DISPATCHED);
        } else if (status.equals("DELIVERED")) {
            drivingLicense.setLicenseStatus(LicenseStatusEnum.DELIVERED);
        }
        drivingLicense.setAddress(drivingLicenseUpdateRequest.address());
        drivingLicenseJpa.save(drivingLicense);
        DrivingLicenseResponse drivingLicenseResponse = DrivingLicenseResponse.builder()
                .id(drivingLicense.getId())
                .userId(currentUser.getId())
                .licenseNumber(drivingLicense.getLicenseNumber())
                .issueDate(drivingLicense.getIssueDate())
                .expirationDate(drivingLicense.getExpirationDate())
                .firstName(drivingLicense.getFirstName())
                .lastName(drivingLicense.getLastName())
                .vehicleType(drivingLicense.getVehicleType())
                .vehicleMake(drivingLicense.getVehicleMake())
                .licenseStatus(drivingLicense.getLicenseStatus().toString())
                .address(drivingLicense.getAddress())
                .build();
        return drivingLicenseResponse;
    }

    @TraceStuff("changeAddressService")
    @Override
    public DrivingLicenseResponse changeAddress(String address) {
        User currentUser = (User) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
        DrivingLicense drivingLicense = drivingLicenseJpa.findByUserId(currentUser.getId());
        drivingLicense.setAddress(address);
        drivingLicenseJpa.save(drivingLicense);
        DrivingLicenseResponse drivingLicenseResponse = DrivingLicenseResponse.builder()
                .id(drivingLicense.getId())
                .userId(currentUser.getId())
                .licenseNumber(drivingLicense.getLicenseNumber())
                .issueDate(drivingLicense.getIssueDate())
                .expirationDate(drivingLicense.getExpirationDate())
                .firstName(drivingLicense.getFirstName())
                .lastName(drivingLicense.getLastName())
                .vehicleType(drivingLicense.getVehicleType())
                .vehicleMake(drivingLicense.getVehicleMake())
                .licenseStatus(drivingLicense.getLicenseStatus().toString())
                .address(drivingLicense.getAddress())
                .build();
        return drivingLicenseResponse;
    }

    @TraceStuff("renewLicenseService")
    @Override
    public DrivingLicenseResponse renewLicense() {
        User currentUser = (User) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
        DrivingLicense drivingLicense = drivingLicenseJpa.findByUserId(currentUser.getId());
        drivingLicense.setIssueDate(new Date());
        System.out.println("=========Renewal Date: " + drivingLicense.getIssueDate());
        drivingLicense.setExpirationDate(new Date(System.currentTimeMillis() + 365 * 24 * 60 * 60 * 1000));
        drivingLicenseJpa.save(drivingLicense);
        DrivingLicenseResponse drivingLicenseResponse = DrivingLicenseResponse.builder()
                .id(drivingLicense.getId())
                .userId(currentUser.getId())
                .licenseNumber(drivingLicense.getLicenseNumber())
                .issueDate(drivingLicense.getIssueDate())
                .expirationDate(drivingLicense.getExpirationDate())
                .firstName(drivingLicense.getFirstName())
                .lastName(drivingLicense.getLastName())
                .vehicleType(drivingLicense.getVehicleType())
                .vehicleMake(drivingLicense.getVehicleMake())
                .licenseStatus(drivingLicense.getLicenseStatus().toString())
                .address(drivingLicense.getAddress())
                .build();

        return drivingLicenseResponse;
    }

    @TraceStuff("changeVehicleService")
    @Override
    public DrivingLicenseResponse changeVehicle(String vehicleBrand, String vehicleType) {
        User currentUser = (User) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
        DrivingLicense drivingLicense = drivingLicenseJpa.findByUserId(currentUser.getId());
        drivingLicense.setVehicleMake(vehicleBrand);
        drivingLicense.setVehicleType(vehicleType);
        drivingLicenseJpa.save(drivingLicense);
        DrivingLicenseResponse drivingLicenseResponse = DrivingLicenseResponse.builder()
                .id(drivingLicense.getId())
                .userId(currentUser.getId())
                .licenseNumber(drivingLicense.getLicenseNumber())
                .issueDate(drivingLicense.getIssueDate())
                .expirationDate(drivingLicense.getExpirationDate())
                .firstName(drivingLicense.getFirstName())
                .lastName(drivingLicense.getLastName())
                .vehicleType(drivingLicense.getVehicleType())
                .vehicleMake(drivingLicense.getVehicleMake())
                .licenseStatus(drivingLicense.getLicenseStatus().toString())
                .address(drivingLicense.getAddress())
                .build();
        return drivingLicenseResponse;
    }


    private String generateLicenseNumber(Integer userId) {
        Tracer tracer = GlobalOpenTelemetry.getTracer("dl-creator-backend");
        Span span = tracer.spanBuilder("generateLicenseNumber").startSpan();

        try (Scope scope = span.makeCurrent()) {
            Random random = new Random();
            int randomDigits = random.nextInt(900000);

            String license = "DL-" + userId + "-" + System.currentTimeMillis() + randomDigits;
            span.setAttribute("user.id", userId);
            span.setAttribute("generated.license", license);

            return license;
        } catch (Exception e) {
            span.recordException(e);
            throw e;
        } finally {
            span.end();
        }
    }

}