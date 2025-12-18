/**
 * NodeBlack JavaScript SDK
 * Universal File Converter API Client
 * 
 * Installation:
 *   npm install axios form-data
 * 
 * Usage:
 *   const NodeBlackClient = require('./nodeblack-sdk');
 *   
 *   const client = new NodeBlackClient('your-api-key');
 *   const result = await client.convertFile('image.png', 'jpg');
 *   await client.downloadFile(result.task_id, 'converted.jpg');
 */

const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');
const path = require('path');

class NodeBlackClient {
    constructor(apiKey, baseUrl = 'https://nodeblack.onrender.com') {
        this.apiKey = apiKey;
        this.baseUrl = baseUrl.replace(/\/$/, '');
        this.client = axios.create({
            baseURL: this.baseUrl,
            headers: {
                'X-API-Key': apiKey
            }
        });
    }

    /**
     * Convert a file to target format
     * @param {string} filePath - Path to input file
     * @param {string} targetFormat - Target format (e.g., 'jpg', 'png', 'mp3')
     * @param {number} timeout - Max wait time in seconds (default: 60)
     * @returns {Promise<Object>} Result with task_id and status
     */
    async convertFile(filePath, targetFormat, timeout = 60) {
        if (!fs.existsSync(filePath)) {
            throw new Error(`File not found: ${filePath}`);
        }

        const formData = new FormData();
        formData.append('file', fs.createReadStream(filePath));

        try {
            const response = await this.client.post('/api/convert', formData, {
                params: { target_format: targetFormat },
                headers: formData.getHeaders()
            });

            const { task_id } = response.data;
            return await this._waitForCompletion(task_id, timeout);

        } catch (error) {
            throw new Error(`Conversion failed: ${error.response?.data?.detail || error.message}`);
        }
    }

    /**
     * Wait for conversion to complete
     * @private
     */
    async _waitForCompletion(taskId, timeout) {
        const startTime = Date.now();

        while (Date.now() - startTime < timeout * 1000) {
            const status = await this.getStatus(taskId);

            if (status.status === 'ready') {
                return { task_id: taskId, status: 'completed' };
            } else if (['failed', 'expired'].includes(status.status)) {
                throw new Error(`Conversion failed: ${status.message || 'Unknown error'}`);
            }

            await new Promise(resolve => setTimeout(resolve, 1000));
        }

        throw new Error(`Conversion timeout after ${timeout} seconds`);
    }

    /**
     * Get conversion status
     * @param {string} taskId - Task ID
     * @returns {Promise<Object>} Status information
     */
    async getStatus(taskId) {
        try {
            const response = await this.client.get(`/api/status/${taskId}`);
            return response.data;
        } catch (error) {
            throw new Error(`Status check failed: ${error.response?.data?.detail || error.message}`);
        }
    }

    /**
     * Download converted file
     * @param {string} taskId - Task ID
     * @param {string} outputPath - Output file path
     * @returns {Promise<string>} Path to downloaded file
     */
    async downloadFile(taskId, outputPath) {
        try {
            const response = await this.client.get(`/api/download/${taskId}`, {
                responseType: 'stream'
            });

            // Ensure output directory exists
            const outputDir = path.dirname(outputPath);
            if (!fs.existsSync(outputDir)) {
                fs.mkdirSync(outputDir, { recursive: true });
            }

            // Write file
            const writer = fs.createWriteStream(outputPath);
            response.data.pipe(writer);

            return new Promise((resolve, reject) => {
                writer.on('finish', () => resolve(outputPath));
                writer.on('error', reject);
            });

        } catch (error) {
            throw new Error(`Download failed: ${error.response?.data?.detail || error.message}`);
        }
    }

    /**
     * Get all supported formats
     * @returns {Promise<Object>} Supported formats
     */
    async getSupportedFormats() {
        try {
            const response = await this.client.get('/api/formats');
            return response.data;
        } catch (error) {
            throw new Error(`Failed to get formats: ${error.response?.data?.detail || error.message}`);
        }
    }

    /**
     * List all converted files
     * @returns {Promise<Object>} List of files
     */
    async listFiles() {
        try {
            const response = await this.client.get('/api/files');
            return response.data;
        } catch (error) {
            throw new Error(`Failed to list files: ${error.response?.data?.detail || error.message}`);
        }
    }
}

module.exports = NodeBlackClient;

// Example usage
if (require.main === module) {
    (async () => {
        const client = new NodeBlackClient('your-api-key-here');

        try {
            // Convert image
            console.log('🔄 Converting file...');
            const result = await client.convertFile('input.png', 'jpg');
            console.log('✅ Conversion completed:', result);

            // Download result
            console.log('⬇️ Downloading file...');
            const outputFile = await client.downloadFile(result.task_id, 'output.jpg');
            console.log('✅ Downloaded:', outputFile);

        } catch (error) {
            console.error('❌ Error:', error.message);
        }
    })();
}