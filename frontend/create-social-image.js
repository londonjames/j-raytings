// Script to create social sharing images with padding around quilts
import fs from 'fs';
import { createCanvas, loadImage } from 'canvas';

// Social media recommended dimensions
// LinkedIn: 1200x627 (1.91:1)
// Twitter: 1200x675 (16:9)
// We'll use 1200x675 for better compatibility
const SOCIAL_WIDTH = 1200;
const SOCIAL_HEIGHT = 675;
const QUILT_SCALE = 0.80; // Quilt takes up 80% of the image (5% smaller)
const BACKGROUND_COLOR = '#f0f0f0'; // Lighter gray background

async function createSocialImage(quiltPath, outputPath) {
  try {
    // Load the original quilt image
    const quilt = await loadImage(quiltPath);
    
    // Calculate dimensions for the quilt (75% of the social image)
    const maxQuiltWidth = SOCIAL_WIDTH * QUILT_SCALE;
    const maxQuiltHeight = SOCIAL_HEIGHT * QUILT_SCALE;
    
    // Maintain aspect ratio
    let quiltWidth, quiltHeight;
    const quiltAspect = quilt.width / quilt.height;
    const maxAspect = maxQuiltWidth / maxQuiltHeight;
    
    if (quiltAspect > maxAspect) {
      // Quilt is wider - fit to width
      quiltWidth = maxQuiltWidth;
      quiltHeight = maxQuiltWidth / quiltAspect;
    } else {
      // Quilt is taller - fit to height
      quiltHeight = maxQuiltHeight;
      quiltWidth = maxQuiltHeight * quiltAspect;
    }
    
    // Center the quilt in the social image
    const x = (SOCIAL_WIDTH - quiltWidth) / 2;
    const y = (SOCIAL_HEIGHT - quiltHeight) / 2;
    
    // Create canvas
    const canvas = createCanvas(SOCIAL_WIDTH, SOCIAL_HEIGHT);
    const ctx = canvas.getContext('2d');
    
    // Fill with gray background
    ctx.fillStyle = BACKGROUND_COLOR;
    ctx.fillRect(0, 0, SOCIAL_WIDTH, SOCIAL_HEIGHT);
    
    // Set up drop shadow (more pronounced)
    ctx.shadowColor = 'rgba(0, 0, 0, 0.4)';
    ctx.shadowBlur = 30;
    ctx.shadowOffsetX = 0;
    ctx.shadowOffsetY = 8;
    
    // Draw the quilt image centered with drop shadow
    ctx.drawImage(quilt, x, y, quiltWidth, quiltHeight);
    
    // Reset shadow for any future drawing
    ctx.shadowColor = 'transparent';
    ctx.shadowBlur = 0;
    ctx.shadowOffsetX = 0;
    ctx.shadowOffsetY = 0;
    
    // Save as JPEG
    const buffer = canvas.toBuffer('image/jpeg', { quality: 0.95 });
    fs.writeFileSync(outputPath, buffer);
    
    console.log(`Created ${outputPath}`);
    console.log(`  Original quilt: ${quilt.width}x${quilt.height}`);
    console.log(`  Scaled quilt: ${Math.round(quiltWidth)}x${Math.round(quiltHeight)}`);
    console.log(`  Position: x=${Math.round(x)}, y=${Math.round(y)}`);
    console.log(`  Social image: ${SOCIAL_WIDTH}x${SOCIAL_HEIGHT}`);
    
    return true;
  } catch (error) {
    console.error(`Error creating social image: ${error.message}`);
    return false;
  }
}

// Create books social image
const booksQuiltPath = 'public/books-quilt.jpg';
const booksOutputPath = 'public/books-quilt-social.jpg';

// Create films social image
const filmsQuiltPath = 'public/films-quilt.jpg';
const filmsOutputPath = 'public/films-quilt-social.jpg';

Promise.all([
  createSocialImage(booksQuiltPath, booksOutputPath),
  createSocialImage(filmsQuiltPath, filmsOutputPath)
])
  .then(results => {
    const [booksSuccess, filmsSuccess] = results;
    if (booksSuccess && filmsSuccess) {
      console.log('\n✅ Both social images created successfully!');
    } else {
      if (!booksSuccess) console.log('\n❌ Failed to create books social image');
      if (!filmsSuccess) console.log('\n❌ Failed to create films social image');
      process.exit(1);
    }
  })
  .catch(error => {
    console.error('Error:', error);
    process.exit(1);
  });

