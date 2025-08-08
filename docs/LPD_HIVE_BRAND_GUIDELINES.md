# LPD Hive Brand Guidelines

## Brand Colors

### Primary Palette
- **Orange (Creative Impulse)**: `#FA4616` - Pantone 172C
  - Represents creation, innovation, and creative energy
  - Used for primary actions, highlights, and brand emphasis
  
- **Wine (Strategy)**: `#551C25` - Pantone 4102C  
  - Represents strategic thinking and planning
  - Used for secondary elements and professional accents
  
- **Black (Structure)**: `#25282A` - Pantone 426C
  - Represents organization and structure
  - Used for text, backgrounds, and UI structure
  
- **Off-white (Clarity)**: `#E7E7E0` - Pantone 9100C
  - Represents clarity and transparency
  - Used for light backgrounds and contrast elements

## Typography

### Primary Fonts
- **Headlines/Titles**: Glancyr Neue
  - Modern, clean, professional appearance
  - Use for all headings (h1-h6) and brand text
  
- **Body Text**: Poppins
  - Excellent readability for interfaces
  - Use for all paragraph text, UI elements, and general content

### Implementation
```css
/* Headlines */
font-family: 'Glancyr Neue', 'Poppins', -apple-system, sans-serif;

/* Body Text */
font-family: 'Poppins', -apple-system, BlinkMacSystemFont, sans-serif;
```

## Logo System

The LPD Hive logo is based on a hexagonal beehive structure, representing:
- **Hexagon**: Efficiency, organization, and perfect structure
- **Beehive**: Collaboration, productivity, and collective intelligence
- **Orange accent**: Creative energy and innovation

## Brand Values

1. **Transformação** (Transformation)
2. **Inovação** (Innovation)  
3. **Coragem** (Courage)
4. **Simplicidade** (Simplicity)
5. **Ordem** (Order)

## Brand Essence

**"Inteligência em movimento, transformando dados em decisões"**
(Intelligence in motion, transforming data into decisions)

## UI Implementation Notes

### CSS Variables
```css
:root {
    --lpd-orange: #FA4616;
    --lpd-wine: #551C25;
    --lpd-black: #25282A;
    --lpd-offwhite: #E7E7E0;
}
```

### Usage Guidelines
- Use orange sparingly for emphasis and CTAs
- Maintain high contrast for accessibility
- Wine color for secondary actions and professional elements
- Black for primary text and structural elements
- Off-white for backgrounds and light themes

## Files Updated

The following files have been updated to comply with brand guidelines:

1. **src/dlq_monitor/web/static/css/lpd-hive.css**
   - Updated color variables to official brand colors
   - Added brand typography definitions
   - Maintained dark theme with brand accents

2. **src/dlq_monitor/web/templates/dashboard.html**
   - Added Google Fonts link for Poppins
   - Ensures proper font loading

## Additional Notes

- The neurocenter.css file already uses the correct brand orange (#FA4616)
- The neurocenter-modern.css uses a different cyber/neon theme and is intentionally separate
- All future UI components should reference these brand colors via CSS variables