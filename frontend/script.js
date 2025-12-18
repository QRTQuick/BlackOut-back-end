// Configuration
const API_BASE_URL = 'https://nodeblack.onrender.com';
const API_KEY = 'blackout-secret-key';

// Global variables
let selectedFile = null;
let selectedFormat = null;
let currentTaskId = null;

// Format mappings
const formatMappings = {
    // Images
    'image': ['png', 'jpg', 'jpeg', 'webp', 'bmp', 'tiff', 'gif'],
    // Audio
    'audio': ['mp3', 'wav', 'ogg', 'flac', 'aac', 'm4a'],
    // Video
    'video': ['mp4', 'avi', 'mov', 'webm', 'gif'],
    // Documents
    'document': ['pdf', 'docx', 'txt'],
    // Spreadsheets
    'spreadsheet': ['csv', 'xlsx', 'xls', 'json', 'html'],
    // Presentations
    'presentation': ['pptx', 'txt', 'json']
};

const fileIcons = {
    // Images
    'png': 'fas fa-image', 'jpg': 'fas fa-image', 'jpeg': 'fas fa-image', 
    'webp': 'fas fa-image', 'bmp': 'fas fa-image', 'tiff': 'fas fa-image', 'gif': 'fas fa-image',
    // Audio
    'mp3': 'fas fa-music', 'wav': 'fas fa-music', 'ogg': 'fas fa-music', 
    'flac': 'fas fa-music', 'aac': 'fas fa-music', 'm4a': 'fas fa-music',
    // Video
    'mp4': 'fas fa-video', 'avi': 'fas fa-video', 'mov': 'fas fa-video', 
    'webm': 'fas fa-video', 'mkv': 'fas fa-video', 'flv': 'fas fa-video',
    // Documents
    'pdf': 'fas fa-file-pdf', 'docx': 'fas fa-file-word', 'txt': 'fas fa-file-alt',
    // Spreadsheets
    'csv': 'fas fa-file-csv', 'xlsx': 'fas fa-file-excel', 'xls': 'fas fa-file-excel',
    'json': 'fas fa-file-code', 'html': 'fas fa-file-code',
    // Presentations
    'pptx': 'fas fa-file-powerpoint'
};

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    setupDragAndDrop();
});

function initializeEventListeners() {
    const fileInput = document.getElementById('fileInput');
    fileInput.addEventListener('change', handleFileSelect);
}

function setupDragAndDrop() {
    const uploadArea = document.getElementById('uploadArea');
    
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });
    
    uploadArea.addEventListener('click', () => {
        document.getElementById('fileInput').click();
    });
}

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        handleFile(file);
    }
}

function handleFile(file) {
    selectedFile = file;
    
    // Update file info
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    const fileType = document.getElementById('fileType');
    const fileIcon = document.getElementById('fileIcon');
    
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    fileType.textContent = file.type || 'Unknown type';
    
    // Set appropriate icon
    const extension = getFileExtension(file.name);
    const iconClass = fileIcons[extension] || 'fas fa-file';
    fileIcon.className = iconClass;
    
    // Show file info and format selection
    document.getElementById('fileInfo').style.display = 'block';
    document.getElementById('formatSection').style.display = 'block';
    
    // Generate format options
    generateFormatOptions(extension);
    
    // Add fade-in animation
    document.getElementById('fileInfo').classList.add('fade-in');
    document.getElementById('formatSection').classList.add('fade-in');
}

function generateFormatOptions(inputExtension) {
    const formatGrid = document.getElementById('formatGrid');
    formatGrid.innerHTML = '';
    
    // Determine file category
    let availableFormats = [];
    
    if (['png', 'jpg', 'jpeg', 'webp', 'bmp', 'tiff', 'gif'].includes(inputExtension)) {
        availableFormats = formatMappings.image.filter(f => f !== inputExtension);
    } else if (['mp3', 'wav', 'ogg', 'flac', 'aac', 'm4a'].includes(inputExtension)) {
        availableFormats = formatMappings.audio.filter(f => f !== inputExtension);
    } else if (['mp4', 'avi', 'mov', 'webm', 'mkv', 'flv'].includes(inputExtension)) {
        availableFormats = [...formatMappings.video, 'mp3', 'wav'].filter(f => f !== inputExtension);
    } else if (['csv', 'xlsx', 'xls'].includes(inputExtension)) {
        availableFormats = formatMappings.spreadsheet.filter(f => f !== inputExtension);
    } else if (inputExtension === 'pptx') {
        availableFormats = ['txt', 'json'];
    } else if (inputExtension === 'txt') {
        availableFormats = ['docx', 'pptx'];
    } else if (inputExtension === 'pdf') {
        availableFormats = ['docx'];
    }
    
    // Create format options
    availableFormats.forEach(format => {
        const formatOption = document.createElement('div');
        formatOption.className = 'format-option';
        formatOption.onclick = () => selectFormat(format, formatOption);
        
        const icon = document.createElement('i');
        icon.className = fileIcons[format] || 'fas fa-file';
        
        const label = document.createElement('span');
        label.textContent = format.toUpperCase();
        
        formatOption.appendChild(icon);
        formatOption.appendChild(label);
        formatGrid.appendChild(formatOption);
    });
}

function selectFormat(format, element) {
    // Remove previous selection
    document.querySelectorAll('.format-option').forEach(option => {
        option.classList.remove('selected');
    });
    
    // Select current
    element.classList.add('selected');
    selectedFormat = format;
    
    // Show convert button
    document.getElementById('convertSection').style.display = 'block';
    document.getElementById('convertSection').classList.add('fade-in');
}

async function convertFile() {
    if (!selectedFile || !selectedFormat) {
        showNotification('Please select a file and format', 'error');
        return;
    }
    
    const convertBtn = document.getElementById('convertBtn');
    const progressSection = document.getElementById('progressSection');
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    
    // Show progress
    convertBtn.disabled = true;
    convertBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Converting...';
    progressSection.style.display = 'block';
    document.getElementById('progressFill').style.width = '0%';
    progressText.textContent = 'Uploading file...';
    
    try {
        // Upload file
        const formData = new FormData();
        formData.append('file', selectedFile);
        
        const response = await fetch(`${API_BASE_URL}/api/convert?target_format=${selectedFormat}`, {
            method: 'POST',
            headers: {
                'X-API-Key': API_KEY
            },
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        currentTaskId = result.task_id;
        
        progressText.textContent = 'Processing...';
        document.getElementById('progressFill').style.width = '50%';
        
        // Poll for completion
        await pollConversionStatus();
        
    } catch (error) {
        console.error('Conversion error:', error);
        showNotification('Conversion failed: ' + error.message, 'error');
        resetConversion();
    }
}

async function pollConversionStatus() {
    const maxAttempts = 60; // 60 seconds timeout
    let attempts = 0;
    
    const poll = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/status/${currentTaskId}`);
            const status = await response.json();
            
            if (status.status === 'ready') {
                document.getElementById('progressFill').style.width = '100%';
                document.getElementById('progressText').textContent = 'Conversion complete!';
                showDownloadButton();
                showNotification('File converted successfully!', 'success');
            } else if (status.status === 'failed' || status.status === 'expired') {
                throw new Error(status.message || 'Conversion failed');
            } else if (attempts < maxAttempts) {
                attempts++;
                setTimeout(poll, 1000); // Poll every second
            } else {
                throw new Error('Conversion timeout');
            }
        } catch (error) {
            showNotification('Status check failed: ' + error.message, 'error');
            resetConversion();
        }
    };
    
    poll();
}

function showDownloadButton() {
    const resultSection = document.getElementById('resultSection');
    const downloadBtn = document.getElementById('downloadBtn');
    
    resultSection.style.display = 'block';
    resultSection.classList.add('fade-in');
    
    // Add click event to download button
    downloadBtn.onclick = downloadFile;
}

async function downloadFile() {
    if (!currentTaskId) {
        showNotification('No file to download', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/download/${currentTaskId}`);
        
        if (!response.ok) {
            throw new Error(`Download failed: ${response.status}`);
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `converted_${currentTaskId}.${selectedFormat}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        showNotification('File downloaded successfully!', 'success');
        
    } catch (error) {
        showNotification('Download failed: ' + error.message, 'error');
    }
}

function resetConversion() {
    const convertBtn = document.getElementById('convertBtn');
    convertBtn.disabled = false;
    convertBtn.innerHTML = '<i class="fas fa-magic"></i> Convert File';
    
    document.getElementById('progressSection').style.display = 'none';
    document.getElementById('resultSection').style.display = 'none';
    
    currentTaskId = null;
}

function resetForm() {
    // Reset all states
    selectedFile = null;
    selectedFormat = null;
    currentTaskId = null;
    
    // Hide sections
    document.getElementById('fileInfo').style.display = 'none';
    document.getElementById('formatSection').style.display = 'none';
    document.getElementById('convertSection').style.display = 'none';
    document.getElementById('progressSection').style.display = 'none';
    document.getElementById('resultSection').style.display = 'none';
    
    // Reset file input
    document.getElementById('fileInput').value = '';
    
    // Reset convert button
    resetConversion();
}

function removeFile() {
    resetForm();
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Trigger animation
    setTimeout(() => notification.classList.add('show'), 100);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => document.body.removeChild(notification), 300);
    }, 3000);
}

function getFileExtension(filename) {
    return filename.split('.').pop().toLowerCase();
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// API Status Check
async function checkAPIStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/test`);
        const status = await response.json();
        
        if (status.status === 'working') {
            showNotification('Connected to NodeBlack API', 'success');
        }
    } catch (error) {
        showNotification('API connection failed', 'error');
    }
}

// Check API status on load
checkAPIStatus();