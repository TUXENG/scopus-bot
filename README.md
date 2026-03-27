# Create the markdown file for the user to download

content = """# Scopus Bot - Estado del Proyecto

## 🧠 Descripción General
Proyecto para automatizar Scopus con Playwright:
- Navegación institucional
- Login
- Acceso a Scopus
- Búsqueda
- Filtros
- Scraping
- Preparación de datos

## ⚙️ Stack
- Python
- Playwright (sync)
- Arquitectura modular

## 🎯 Filtros
### Subject Area
- Engineering
- Materials Science
- Environmental Science
- Earth and Planetary Sciences

### Document Type
- Article
- Review
- Conference paper

## 🧱 Modelo de Datos
- title
- doc_type
- authors
- source
- year
- citations
- doi (link Scopus)

## 🔁 Flujo
1. Buscar
2. Configurar resultados
3. Aplicar subject area
4. Loop por document type
5. Scraping
6. Deduplicación

## 📊 Estado
✔ Todo funcional hasta scraping + deduplicación

## 🚀 Próximos pasos
- Exportar a Excel
- Paginación


