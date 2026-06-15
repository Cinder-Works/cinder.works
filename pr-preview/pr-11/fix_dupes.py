import re

# Fix index.html CSS dupes
with open('index.html', 'r') as f:
    content = f.read()

# The CSS block starts with .visually-hidden
css_block = """
    .visually-hidden {
      position: absolute;
      width: 1px;
      height: 1px;
      padding: 0;
      margin: -1px;
      overflow: hidden;
      clip: rect(0, 0, 0, 0);
      white-space: nowrap;
      border: 0;
    }

    :focus-visible {
      outline: 2px solid #ff7a45;
      outline-offset: 2px;
    }

    @media (prefers-reduced-motion: reduce) {
      .heartbeat-trigger,
      .heart-particle {
        animation: none !important;
      }
      .modal, .modal-overlay {
        transition: none !important;
      }
    }
"""

# Replace all occurrences of this CSS block with a single one (since they are together at the end of style)
content = re.sub(re.escape(css_block.strip()) + r'\s+' + re.escape(css_block.strip()), css_block.strip(), content)

# Also fix the JS duplicate
js_block = """  // ========================================
  // Heartbeat trigger keyboard access
  // ========================================
  document.addEventListener('DOMContentLoaded', function() {
    var triggers = document.querySelectorAll('.heartbeat-trigger');
    for (var i = 0; i < triggers.length; i++) {
      triggers[i].setAttribute('tabindex', '0');
      triggers[i].setAttribute('role', 'button');
      triggers[i].addEventListener('keydown', function(e) {
        if (e.key === 'Enter' || e.key === ' ') {
          if (e.key === ' ') e.preventDefault();
          if (this.id === 'heartbeatTrigger') {
            triggerHeartbeat(e);
          } else {
            triggerSoul(e);
          }
        }
      });
    }
  });"""

content = re.sub(re.escape(js_block.strip()) + r'\s*' + re.escape(js_block.strip()), js_block.strip(), content)

with open('index.html', 'w') as f:
    f.write(content)


# Fix assets/cinder-triggers.css
with open('assets/cinder-triggers.css', 'r') as f:
    content = f.read()

css_block2 = """
.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

:focus-visible {
  outline: 2px solid #ff7a45;
  outline-offset: 2px;
}

@media (prefers-reduced-motion: reduce) {
  .cinder-particle {
    animation: none !important;
  }
  .cinder-modal-overlay,
  .cinder-modal {
    transition: none !important;
  }
}
"""

content = re.sub(re.escape(css_block2.strip()) + r'\s+' + re.escape(css_block2.strip()), css_block2.strip() + "\n\n", content)

with open('assets/cinder-triggers.css', 'w') as f:
    f.write(content)
