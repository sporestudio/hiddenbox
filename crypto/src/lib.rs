/*
* ---- HiddenBox Project ---- *
*
* src/cryto.rs
* Library to encrypt/desencrypt files
*
* Author: Jorge Rodríguez Castillo
*/

use aes_gcm::{
    aead::{Aead, AeadCore, KeyInit, OsRng},
    Aes256Gcm, Key, Nonce,
};

use anyhow::{anyhow, Result};
use base64::{engine::general_purpose, Engine as _};
use pyo3::exceptions::{PyIOError, PyValueError};
use pyo3::prelude::*;
use rand::Rng;
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::fs::{self, File};
use std::io::{Read, Write};
use std::path::Path;
use uuid::Uuid;


// Files metadata structure
#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct ChunkInfo {
    pub chunk_id: String,
    pub order: usize,
    pub size: usize,
    pub hash: String,
    pub storage_location: String,
}

#[derive(Serialize, Deserialize, Debug, Clone)] 
pub struct Metadata {
    pub original_name: String,
    pub file_id: String,
    pub total_size: usize,
    pub total_chunks: usize,
    pub chunk_size: usize,
    pub encryption_key: String,
    pub nonce: String,
    pub chunks: Vec<ChunkInfo>,
}


// Class for the encryptation service
#[pyclass]
pub struct EncryptionService {
    chunk_size: usize,
}

#[pymethods]
impl EncryptionService {
    #[new]
    pub fn new(chunk_size: usize) -> Self {
        EncryptionService { chunk_size }
    }

    // Available methods for python

    // Cipher and fragment a file
    #[pyo3(text_signature = "($self, file_path, output_dir)")]
    pub fn encrypt_fragment_file(&self, file_path: &str, output_dir: &str) -> PyResult<String> {
        match self._encrypt_fragment_file(file_path, output_dir) { // TODO: Fix this shit, not defined in the EcryptionService yet.
            Ok(metadata) => {
                let json = serde_json::to_string(&metadata)
                    .map_err(|e| PyValueError::new_err(format!("Error serializing metadata: {}", e)))?;
                Ok(json)
            }
            Err(e) => Err(PyIOError::new_err(format!("Error to cipher and fragment: {}", e))),
        }
    }
}


// Internal implementation, not exposed to python API service
impl EncryptionService {
    fn encrypt_data(&self, data: &[u8], key: &[u8]) -> Result<(Vec<u8>, Vec<u8>)> {
        let key = Key::<Aes256Gcm>::from_slice(key);
        let cipher = Aes256Gcm::new(key);

        let nonce = Aes256Gcm::generate_nonce(&mut OsRng);
        let ciphertext = cipher.encrypt(&nonce, data)
            .map_err(|e| anyhow!("Cipher error: {}", e))?;

        Ok((ciphertext, nonce.to_vec()))
    }
}

