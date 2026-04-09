# YBTM Component Documentation

## Quick Reference for Token-Efficient Editing

---

## Navigation Component
**File**: `index.html:600-610`
**Status**: LOCKED

```html
<ul class="nav-links">
    <li><a href="#home">Home</a></li>
    <li><a href="#services">Services</a></li>
    <li><a href="#books">Library</a></li>
    <li><a href="about.html">About Us</a></li>
    <li><a href="#contact">Connect</a></li>
</ul>
```

---

## Hero Component
**File**: `index.html:615-630`
**Status**: LOCKED

```html
<section class="hero" id="home">
    <div class="hero-content">
        <div class="hero-badge">Financial Sovereignty</div>
        <h1>You Became The Money</h1>
        <p class="hero-subtitle">From Goods to Gods</p>
        <p class="hero-description">...</p>
        <a href="#services" class="btn btn-primary">Explore Services</a>
    </div>
</section>
```

---

## Services Component
**File**: `index.html:635-750`
**Status**: LOCKED
**Features**: 3 pillars with dropdown

---

## Books Component
**File**: `index.html:755-850`
**Status**: LOCKED
**Count**: 8 Amazon books

Book List:
1. Black's Law Dictionary
2. Maritime Liens and Claims
3. Conflict of Laws
4. Administrative Law
5. Corpus Juris Secundum
6. Creditors and Their Bonds
7. Corbin on Contracts
8. You Became The Money

---

## Free Ebook Component
**File**: `index.html:855-880`
**Status**: LOCKED
**IMPORTANT**: Standalone centered section

---

## Expertise Component
**File**: `index.html:885-950`
**Status**: LOCKED
**Features**: 6 areas of mastery

---

## Contact Component
**File**: `index.html:955-1000`
**Status**: LOCKED

---

## Music Player Component
**File**: `index.html:1005-1050`
**Status**: LOCKED
**Position**: bottom-left
**Integrations**: SoundCloud

---

## ElevenLabs Voice Agent Component
**File**: `index.html:1055-1060`
**Status**: LOCKED
**Position**: bottom-right
**Agent ID**: agent_2401kh49ezxaef3tqynwkb1pyp22

---

## CSS Variables
**File**: `assets/css/main.css`

```css
:root {
    --navy: #0a0e27;
    --navy-light: #1a1f3a;
    --gold: #d4af37;
    --gold-light: #f4d03f;
    --papyrus: #f4e4c1;
    --charcoal: #0a0a0a;
}
```

---

## Token-Saving Commands

```bash
# View any component by line number
sed -n 'START,ENDp' index.html

# Quick component search
grep -n "section.*id=\"COMPONENT\"" index.html

# Check current state
cat .workspace-state.json
```
