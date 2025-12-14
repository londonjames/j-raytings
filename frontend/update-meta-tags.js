// Script to update meta tags in built HTML files for social sharing
import fs from 'fs';
import path from 'path';

const distDir = path.join(process.cwd(), 'dist');

// Meta tag configurations
// Add cache-busting version to force refresh
const CACHE_VERSION = 'v2';

const filmsMeta = {
  title: 'Every film I\'ve seen (1700+)',
  description: 'Browse my collection of over 1700 films I\'ve watched, each with my own J-Rayting. And if you\'re super geeky, you can filter by Rotten Tomatoes score, Year, genre, and more.',
  image: `https://jamesraybould.me/films-quilt-social.jpg?${CACHE_VERSION}`,
  url: 'https://jamesraybould.me/films'
};

const booksMeta = {
  title: 'Every book I\'ve read (700+)',
  description: 'Browse my personal collection of over 700 books I\'ve read, each with my own J-Rayting. And if you\'re super geeky, you can skim my short summaries or even dig into my comprehensive Notion pages with all my Amazon Kindle highlights.',
  image: `https://jamesraybould.me/books-quilt-social.jpg?${CACHE_VERSION}`,
  url: 'https://jamesraybould.me/books'
};

function updateMetaTags(filePath, meta) {
  if (!fs.existsSync(filePath)) {
    console.log(`File not found: ${filePath}`);
    return;
  }

  let html = fs.readFileSync(filePath, 'utf8');

  // Helper function to update or create meta tag
  const updateMeta = (property, content, isProperty = true) => {
    const attribute = isProperty ? 'property' : 'name';
    const regex = new RegExp(`<meta\\s+${attribute}="${property.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}"[^>]*>`, 'i');
    const newTag = `<meta ${attribute}="${property}" content="${content}" />`;
    
    if (regex.test(html)) {
      html = html.replace(regex, newTag);
    } else {
      // Insert before closing </head>
      html = html.replace('</head>', `    ${newTag}\n  </head>`);
    }
  };

  // Update title
  html = html.replace(/<title>.*?<\/title>/i, `<title>${meta.title}</title>`);

  // Update Open Graph tags
  updateMeta('og:type', 'website');
  updateMeta('og:url', meta.url);
  updateMeta('og:title', meta.title);
  updateMeta('og:description', meta.description);
  updateMeta('og:image', meta.image);

  // Update Twitter Card tags
  updateMeta('twitter:card', 'summary_large_image', false);
  updateMeta('twitter:url', meta.url, false);
  updateMeta('twitter:title', meta.title, false);
  updateMeta('twitter:description', meta.description, false);
  updateMeta('twitter:image', meta.image, false);

  fs.writeFileSync(filePath, html, 'utf8');
  console.log(`Updated meta tags in ${filePath}`);
}

// Update films.html
const filmsPath = path.join(distDir, 'films.html');
updateMetaTags(filmsPath, filmsMeta);

// Update books.html
const booksPath = path.join(distDir, 'books.html');
updateMetaTags(booksPath, booksMeta);

console.log('Meta tags updated successfully!');

