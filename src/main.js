import './style.css'

let allBusinesses = []
let filteredBusinesses = []

// DOM elements
const searchInput = document.getElementById('searchInput')
const searchBtn = document.getElementById('searchBtn')
const businessGrid = document.getElementById('businessGrid')
const businessCount = document.getElementById('businessCount')
const loading = document.getElementById('loading')

// Merge and deduplicate datasets
async function mergeDatasets() {
  try {
    loading.style.display = 'block'
    businessGrid.innerHTML = ''
    
    // Load both datasets
    const [response1, response2] = await Promise.all([
      fetch('/miami_businesses.json'),
      fetch('/miami_businesses_test.json')
    ])
    
    const businessesMain = await response1.json()
    const businessesTest = await response2.json()
    
    console.log(`Main dataset: ${businessesMain.length} businesses`)
    console.log(`Test dataset: ${businessesTest.length} businesses`)
    
    // Combine datasets
    const combined = [...businessesMain, ...businessesTest]
    console.log(`Combined dataset: ${combined.length} businesses`)
    
    // Remove duplicates
    const { uniqueBusinesses, duplicatesRemoved } = removeDuplicates(combined)
    
    console.log(`After deduplication: ${uniqueBusinesses.length} businesses`)
    console.log(`Duplicates removed: ${duplicatesRemoved.length}`)
    
    allBusinesses = uniqueBusinesses
    filteredBusinesses = uniqueBusinesses
    
    displayBusinesses(filteredBusinesses)
    updateStats()
    
    loading.style.display = 'none'
  } catch (error) {
    console.error('Error loading business data:', error)
    loading.innerHTML = '<p>Error loading business data</p>'
  }
}

// Remove duplicate businesses
function removeDuplicates(businesses) {
  const seen = new Set()
  const uniqueBusinesses = []
  const duplicatesRemoved = []
  
  businesses.forEach(business => {
    // Create a key combining name and phone for exact matching
    const key = `${business.business_name.trim().toLowerCase()}|${business.phone_number.trim()}`
    
    if (!seen.has(key)) {
      seen.add(key)
      uniqueBusinesses.push(business)
    } else {
      duplicatesRemoved.push(business)
    }
  })
  
  return { uniqueBusinesses, duplicatesRemoved }
}

// Display businesses in grid
function displayBusinesses(businesses) {
  businessGrid.innerHTML = ''
  
  businesses.forEach(business => {
    const businessCard = createBusinessCard(business)
    businessGrid.appendChild(businessCard)
  })
}

// Create business card element
function createBusinessCard(business) {
  const card = document.createElement('div')
  card.className = 'business-card'
  
  card.innerHTML = `
    <div class="business-header">
      <h3 class="business-name">${business.business_name}</h3>
    </div>
    <div class="business-info">
      <div class="phone-number">
        <span class="phone-label">Phone:</span>
        <a href="tel:${business.phone_number}" class="phone-link">${business.phone_number}</a>
      </div>
    </div>
  `
  
  return card
}

// Search functionality
function searchBusinesses(query) {
  if (!query.trim()) {
    filteredBusinesses = allBusinesses
  } else {
    const searchTerm = query.toLowerCase()
    filteredBusinesses = allBusinesses.filter(business => 
      business.business_name.toLowerCase().includes(searchTerm) ||
      business.phone_number.includes(searchTerm)
    )
  }
  
  displayBusinesses(filteredBusinesses)
  updateStats()
}

// Update statistics
function updateStats() {
  businessCount.textContent = `${filteredBusinesses.length} businesses found`
}

// Event listeners
searchInput.addEventListener('input', (e) => {
  searchBusinesses(e.target.value)
})

searchBtn.addEventListener('click', () => {
  searchBusinesses(searchInput.value)
})

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
  mergeDatasets()
})