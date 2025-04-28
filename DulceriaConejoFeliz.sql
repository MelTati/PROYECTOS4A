-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb_conejo_feliz
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema mydb_conejo_feliz
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `mydb_conejo_feliz` DEFAULT CHARACTER SET utf8mb3 ;
USE `mydb_conejo_feliz` ;

-- -----------------------------------------------------
-- Table `mydb_conejo_feliz`.`proveedor`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb_conejo_feliz`.`proveedor` (
  `RFC` VARCHAR(20) NOT NULL,
  `nombre_proveedor` VARCHAR(45) NULL DEFAULT NULL,
  `direccion` VARCHAR(45) NULL DEFAULT NULL,
  `telefono` CHAR(10) NULL DEFAULT NULL,
  `email` VARCHAR(45) NULL DEFAULT NULL,
  PRIMARY KEY (`RFC`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb3;


-- -----------------------------------------------------
-- Table `mydb_conejo_feliz`.`marcas`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb_conejo_feliz`.`marcas` (
  `id_marca` INT NOT NULL AUTO_INCREMENT,
  `nombre_marca` VARCHAR(45) NULL DEFAULT NULL,
  `RFC` VARCHAR(20) NOT NULL,
  PRIMARY KEY (`id_marca`),
  INDEX `fk_marcas_proveedor1_idx` (`RFC` ASC) VISIBLE,
  CONSTRAINT `fk_marcas_proveedor1`
    FOREIGN KEY (`RFC`)
    REFERENCES `mydb_conejo_feliz`.`proveedor` (`RFC`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb3;


-- -----------------------------------------------------
-- Table `mydb_conejo_feliz`.`categorias`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb_conejo_feliz`.`categorias` (
  `id_categorias` INT NOT NULL AUTO_INCREMENT,
  `tipo_categoria` VARCHAR(45) NULL DEFAULT NULL,
  PRIMARY KEY (`id_categorias`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb3;


-- -----------------------------------------------------
-- Table `mydb_conejo_feliz`.`articulos`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb_conejo_feliz`.`articulos` (
  `codigo_articulo` VARCHAR(20) NOT NULL,
  `nombre_articulo` VARCHAR(45) NULL DEFAULT NULL,
  `activacion_articulo` TINYINT(1) NULL DEFAULT NULL,
  `precio_articulo` INT NULL DEFAULT NULL,
  `costo_articulo` INT NULL DEFAULT NULL,
  `id_marca` INT NOT NULL,
  `id_categorias` INT NOT NULL,
  `descr_caracteristicas` TEXT NULL,
  PRIMARY KEY (`codigo_articulo`),
  INDEX `fk_articulos_marcas1_idx` (`id_marca` ASC) VISIBLE,
  INDEX `fk_articulos_categorias1_idx` (`id_categorias` ASC) VISIBLE,
  CONSTRAINT `fk_articulos_marcas1`
    FOREIGN KEY (`id_marca`)
    REFERENCES `mydb_conejo_feliz`.`marcas` (`id_marca`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_articulos_categorias1`
    FOREIGN KEY (`id_categorias`)
    REFERENCES `mydb_conejo_feliz`.`categorias` (`id_categorias`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb3;


-- -----------------------------------------------------
-- Table `mydb_conejo_feliz`.`cliente`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb_conejo_feliz`.`cliente` (
  `id_cliente` INT NOT NULL AUTO_INCREMENT,
  `nombre` VARCHAR(45) NULL DEFAULT NULL,
  `telefono` CHAR(10) NULL DEFAULT NULL,
  PRIMARY KEY (`id_cliente`))
ENGINE = InnoDB
AUTO_INCREMENT = 2
DEFAULT CHARACTER SET = utf8mb3;


-- -----------------------------------------------------
-- Table `mydb_conejo_feliz`.`compras`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb_conejo_feliz`.`compras` (
  `id_compras` INT NOT NULL,
  `RFC` VARCHAR(20) NOT NULL,
  `fecha_compras` DATETIME NULL DEFAULT NULL,
  PRIMARY KEY (`id_compras`),
  INDEX `fk_Compras_Proveedor1_idx` (`RFC` ASC) VISIBLE,
  CONSTRAINT `fk_Compras_Proveedor1`
    FOREIGN KEY (`RFC`)
    REFERENCES `mydb_conejo_feliz`.`proveedor` (`RFC`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb3;


-- -----------------------------------------------------
-- Table `mydb_conejo_feliz`.`detalles_compras`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb_conejo_feliz`.`detalles_compras` (
  `cantidad` INT NULL DEFAULT NULL,
  `subtotal` DECIMAL(10,2) NULL DEFAULT NULL,
  `id_compras` INT NOT NULL,
  `codigo_articulo` VARCHAR(20) NOT NULL,
  PRIMARY KEY (`id_compras`, `codigo_articulo`),
  INDEX `fk_Detalles_compras_Articulos1_idx` (`codigo_articulo` ASC) VISIBLE,
  CONSTRAINT `fk_Detalles_compras_Articulos1`
    FOREIGN KEY (`codigo_articulo`)
    REFERENCES `mydb_conejo_feliz`.`articulos` (`codigo_articulo`),
  CONSTRAINT `fk_Detalles_compras_Compras1`
    FOREIGN KEY (`id_compras`)
    REFERENCES `mydb_conejo_feliz`.`compras` (`id_compras`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb3;


-- -----------------------------------------------------
-- Table `mydb_conejo_feliz`.`roles`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb_conejo_feliz`.`roles` (
  `id_roles` INT NOT NULL,
  `cargo` VARCHAR(45) NULL DEFAULT NULL,
  PRIMARY KEY (`id_roles`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb3;


-- -----------------------------------------------------
-- Table `mydb_conejo_feliz`.`usuarios`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb_conejo_feliz`.`usuarios` (
  `id_usuario` INT NOT NULL,
  `nombre_usuario` VARCHAR(45) NULL DEFAULT NULL,
  `telefono` CHAR(10) NOT NULL,
  `password` CHAR(8) NOT NULL,
  `id_roles` INT NOT NULL,
  PRIMARY KEY (`id_usuario`),
  INDEX `fk_usuarios_roles1_idx` (`id_roles` ASC) VISIBLE,
  CONSTRAINT `fk_usuarios_roles1`
    FOREIGN KEY (`id_roles`)
    REFERENCES `mydb_conejo_feliz`.`roles` (`id_roles`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb3;


-- -----------------------------------------------------
-- Table `mydb_conejo_feliz`.`ventas`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb_conejo_feliz`.`ventas` (
  `id_ventas` INT NOT NULL AUTO_INCREMENT,
  `id_usuario` INT NOT NULL,
  `id_cliente` INT NOT NULL,
  `fecha_venta` VARCHAR(10) NOT NULL,
  PRIMARY KEY (`id_ventas`),
  INDEX `fk_ventas_usuarios1_idx` (`id_usuario` ASC) VISIBLE,
  INDEX `fk_ventas_cliente1_idx` (`id_cliente` ASC) VISIBLE,
  CONSTRAINT `fk_ventas_usuarios1`
    FOREIGN KEY (`id_usuario`)
    REFERENCES `mydb_conejo_feliz`.`usuarios` (`id_usuario`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_ventas_cliente1`
    FOREIGN KEY (`id_cliente`)
    REFERENCES `mydb_conejo_feliz`.`cliente` (`id_cliente`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
AUTO_INCREMENT = 5
DEFAULT CHARACTER SET = utf8mb3;


-- -----------------------------------------------------
-- Table `mydb_conejo_feliz`.`detalles_ventas`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb_conejo_feliz`.`detalles_ventas` (
  `cantidad` INT NULL DEFAULT NULL,
  `subtotal` DECIMAL(10,2) NULL DEFAULT NULL,
  `id_ventas` INT NOT NULL,
  `codigo_articulo` VARCHAR(20) NOT NULL,
  PRIMARY KEY (`id_ventas`, `codigo_articulo`),
  INDEX `fk_detalles_ventas_articulos1_idx` (`codigo_articulo` ASC) VISIBLE,
  CONSTRAINT `fk_detalles_ventas_ventas1`
    FOREIGN KEY (`id_ventas`)
    REFERENCES `mydb_conejo_feliz`.`ventas` (`id_ventas`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_detalles_ventas_articulos1`
    FOREIGN KEY (`codigo_articulo`)
    REFERENCES `mydb_conejo_feliz`.`articulos` (`codigo_articulo`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb3;


-- -----------------------------------------------------
-- Table `mydb_conejo_feliz`.`modo_pago`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb_conejo_feliz`.`modo_pago` (
  `id_modo_pago` INT NOT NULL,
  `tipo` VARCHAR(45) NULL DEFAULT NULL,
  PRIMARY KEY (`id_modo_pago`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb3;


-- -----------------------------------------------------
-- Table `mydb_conejo_feliz`.`ticket`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb_conejo_feliz`.`ticket` (
  `id_ticket` VARCHAR(20) NOT NULL,
  `nombre_establec` VARCHAR(45) NULL DEFAULT NULL,
  `direcc_establec` VARCHAR(45) NULL DEFAULT NULL,
  `id_modo_pago` INT NOT NULL,
  `id_ventas` INT NOT NULL,
  PRIMARY KEY (`id_ticket`),
  INDEX `fk_ticket_modo_pago1_idx` (`id_modo_pago` ASC) VISIBLE,
  INDEX `fk_ticket_ventas1_idx` (`id_ventas` ASC) VISIBLE,
  CONSTRAINT `fk_ticket_modo_pago1`
    FOREIGN KEY (`id_modo_pago`)
    REFERENCES `mydb_conejo_feliz`.`modo_pago` (`id_modo_pago`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_ticket_ventas1`
    FOREIGN KEY (`id_ventas`)
    REFERENCES `mydb_conejo_feliz`.`ventas` (`id_ventas`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb3;


-- -----------------------------------------------------
-- Table `mydb_conejo_feliz`.`movimiento_inventario`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb_conejo_feliz`.`movimiento_inventario` (
  `id_movimiento` INT NOT NULL,
  `codigo_articulo` VARCHAR(20) NOT NULL,
  `tipo_movimiento` VARCHAR(45) NULL,
  `cantidad` INT NULL,
  `fecha_movimiento` VARCHAR(45) NULL,
  PRIMARY KEY (`id_movimiento`),
  INDEX `fk_movimiento_inventario_articulos1_idx` (`codigo_articulo` ASC) VISIBLE,
  CONSTRAINT `fk_movimiento_inventario_articulos1`
    FOREIGN KEY (`codigo_articulo`)
    REFERENCES `mydb_conejo_feliz`.`articulos` (`codigo_articulo`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
