import os
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        for attr, value in attrs:
            if attr in ('href', 'src') and value:
                val = value.split('#')[0].split('?')[0]
                if val.startswith('/') and not val.startswith('//'):
                    self.links.append(val)

def get_local_path(url_path):
    if not url_path.startswith('/'):
        return None
    local_path = url_path[1:]
    if url_path.endswith('/'):
        return os.path.join(local_path, 'index.html') if local_path else 'index.html'

    filename = os.path.basename(local_path)
    if '.' in filename:
        return local_path
    else:
        return local_path + '.html'

def main():
    errors = []
    files_scanned = 0
    links_checked = 0

    repo_root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    os.chdir(repo_root)

    # 1. Walk HTML files
    for root_dir, dirs, files in os.walk('.'):
        # Exclude hidden directories like .git, .github
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        for file in files:
            if file.endswith('.html'):
                files_scanned += 1
                filepath = os.path.normpath(os.path.join(root_dir, file))
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    parser = LinkParser()
                    parser.feed(content)
                    for link in parser.links:
                        links_checked += 1
                        local = get_local_path(link)
                        if local and not os.path.exists(local):
                            errors.append({
                                'source': filepath,
                                'target': link,
                                'resolved_path': local
                            })
                except Exception as e:
                    print(f"Error parsing {filepath}: {e}")

    # 2. Check sitemap.xml
    sitemap_path = 'sitemap.xml'
    if os.path.exists(sitemap_path):
        files_scanned += 1
        try:
            tree = ET.parse(sitemap_path)
            root = tree.getroot()
            for elem in root.iter():
                # Handling namespaces: {http://www.sitemaps.org/schemas/sitemap/0.9}loc
                if elem.tag.endswith('}loc') or elem.tag == 'loc':
                    loc = elem.text
                    if loc and loc.startswith('https://cinder.works/'):
                        links_checked += 1
                        path = loc[len('https://cinder.works'):]
                        if not path.startswith('/'):
                            path = '/' + path
                        local = get_local_path(path)
                        if local and not os.path.exists(local):
                            errors.append({
                                'source': sitemap_path,
                                'target': loc,
                                'resolved_path': local
                            })
        except Exception as e:
            print(f"Error parsing {sitemap_path}: {e}")

    # Print summary
    print(f"Scanned {files_scanned} files.")
    print(f"Checked {links_checked} links/assets.")

    if not errors:
        print("\nSUCCESS: All internal links and sitemap references resolve correctly.")
        sys.exit(0)
    else:
        print("\nERRORS FOUND:")
        for err in errors:
            print(f"  - In {err['source']}:")
            print(f"    Reference: {err['target']}")
            print(f"    Resolved to nonexistent file: {err['resolved_path']}")
        print(f"\nTotal errors: {len(errors)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
