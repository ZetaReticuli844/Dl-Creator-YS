package com.dlyog.dl_creator.repository;

import com.dlyog.dl_creator.model.User;
import org.springframework.data.jpa.repository.JpaRepository;

public interface UserJpa extends JpaRepository<User, Long>{
}
