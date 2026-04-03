import os
import re

# Standard paths to ignore
IGNORE_FILES = ['README.md', 'SABLON.md', 'CONTRIBUTING.md', 'LICENSE', '.gitignore', 'task.md', 'implementation_plan.md', 'walkthrough.md']
IGNORE_DIRS = ['.git', '.github', 'assets', 'scripts', '.gemini']

TEMPLATE_PLACEHOLDER = "Filmin olay örgüsü (plot) nedir?"

def analyze_archive(root_path):
    stats = {}
    total_films = 0
    completed_analyses = 0
    director_counts = {}
    
    for root, dirs, files in os.walk(root_path):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        category = os.path.relpath(root, root_path)
        if category == '.':
            continue
            
        if category not in stats:
            stats[category] = {'total': 0, 'completed': 0}
            
        for file in files:
            if file.endswith('.md') and file not in IGNORE_FILES:
                total_films += 1
                stats[category]['total'] += 1
                
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if TEMPLATE_PLACEHOLDER not in content:
                        completed_analyses += 1
                        stats[category]['completed'] += 1
                        
                        # Extract director
                        dir_match = re.search(r"-\s+\*\*Yönetmen:\*\*\s*(.+)", content)
                        if dir_match:
                            dir_name = dir_match.group(1).strip()
                            if dir_name:
                                director_counts[dir_name] = director_counts.get(dir_name, 0) + 1
                        
    return stats, total_films, completed_analyses, director_counts

def generate_markdown_report(stats, total, completed, director_counts):
    report = "### 📊 Arşiv Sağlık Matrisi (Archive Health Matrix)\n\n"
    report += f"**Toplam Film:** {total} | **Tamamlanan Analiz:** {completed} | **Doluluk Oranı:** %{round((completed/total)*100, 2) if total > 0 else 0}\n\n"
    report += "| Kategori | Toplam | Tamamlanan | İlerleme |\n"
    report += "| :--- | :---: | :---: | :--- |\n"
    
    for cat, data in sorted(stats.items()):
        if data['total'] == 0: continue
        progress = round((data['completed'] / data['total']) * 100)
        bar = "█" * (progress // 10) + "░" * (10 - (progress // 10))
        report += f"| {cat.replace('-', ' ')} | {data['total']} | {data['completed']} | `{bar}` %{progress} |\n"
        
    if director_counts:
        report += "\n### 🎬 Yönetmen Kapsamı (Director Coverage)\n\n"
        sorted_dirs = sorted(director_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        for dir_name, count in sorted_dirs:
            report += f"- **{dir_name}:** {count} Film Analizi\n"
            
    return report

if __name__ == "__main__":
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    stats, total, completed, director_counts = analyze_archive(root_dir)
    report = generate_markdown_report(stats, total, completed, director_counts)
    
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print(report)
    
    with open(os.path.join(root_dir, 'ARCHIVE_STATS.md'), 'w', encoding='utf-8') as f:
        f.write("# 📈 Otomatik Arşiv İstatistikleri\n\n")
        f.write(report)
        f.write(f"\n\n*Son Güncelleme: {os.popen('date /t').read().strip()} {os.popen('time /t').read().strip()}*")
