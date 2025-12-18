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
        availableFormats = [...formatMappings.video, 'mp3', 'w