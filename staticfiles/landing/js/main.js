document.addEventListener('DOMContentLoaded', () => {
  const createToast = (message, type = 'success') => {
    if (!message) return;
    let stack = document.querySelector('.toast-stack');
    if (!stack) {
      stack = document.createElement('div');
      stack.className = 'toast-stack';
      document.body.appendChild(stack);
    }
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    stack.appendChild(toast);
    setTimeout(() => {
      toast.classList.add('is-leaving');
      setTimeout(() => toast.remove(), 350);
    }, 3800);
  };

  const menuButton = document.querySelector('[data-menu-toggle]');
  const menu = document.querySelector('[data-menu]');
  if (menuButton && menu) {
    const syncMenuState = () => {
      const isOpen = menu.classList.contains('is-open');
      menuButton.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
      document.body.classList.toggle('nav-open', isOpen);
    };
    menuButton.setAttribute('aria-expanded', 'false');
    menuButton.addEventListener('click', () => {
      menu.classList.toggle('is-open');
      menuButton.classList.toggle('is-open');
      syncMenuState();
    });
    window.addEventListener('resize', () => {
      if (window.innerWidth > 920 && menu.classList.contains('is-open')) {
        menu.classList.remove('is-open');
        menuButton.classList.remove('is-open');
        syncMenuState();
      }
    });
  }

  const header = document.querySelector('.site-header');
  const updateHeaderState = () => {
    if (!header) return;
    header.classList.toggle('is-scrolled', window.scrollY > 12);
  };
  updateHeaderState();
  window.addEventListener('scroll', updateHeaderState, { passive: true });

  if (menu) {
    menu.querySelectorAll('a').forEach((link) => {
      link.addEventListener('click', () => {
        menu.classList.remove('is-open');
        menuButton && menuButton.classList.remove('is-open');
        menuButton && menuButton.setAttribute('aria-expanded', 'false');
        document.body.classList.remove('nav-open');
      });
    });
  }

  const revealItems = document.querySelectorAll('[data-reveal]');
  if ('IntersectionObserver' in window && revealItems.length) {
    const revealObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          revealObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15 });
    revealItems.forEach((item) => revealObserver.observe(item));
  } else {
    revealItems.forEach((item) => item.classList.add('is-visible'));
  }

  document.querySelectorAll('[data-billing-toggle]').forEach((toggle) => {
    const targetSelector = toggle.getAttribute('data-target');
    const scope = targetSelector ? document.querySelector(targetSelector) : document;
    const buttons = toggle.querySelectorAll('[data-billing]');

    const applyBilling = (mode) => {
      buttons.forEach((btn) => btn.classList.toggle('is-active', btn.dataset.billing === mode));
      (scope || document).querySelectorAll('[data-monthly][data-annual]').forEach((element) => {
        element.textContent = mode === 'annual' ? element.dataset.annual : element.dataset.monthly;
      });
    };

    buttons.forEach((btn) => {
      btn.addEventListener('click', () => applyBilling(btn.dataset.billing));
    });

    const activeButton = toggle.querySelector('.is-active[data-billing]');
    applyBilling(activeButton ? activeButton.dataset.billing : 'monthly');
  });

  document.querySelectorAll('[data-module-tabs]').forEach((tabGroup) => {
    const buttons = tabGroup.querySelectorAll('[data-module]');
    const grid = document.querySelector('[data-module-grid]');
    if (!grid) return;

    buttons.forEach((button) => {
      button.addEventListener('click', () => {
        const current = button.dataset.module;
        buttons.forEach((btn) => btn.classList.toggle('is-active', btn === button));

        grid.querySelectorAll('[data-category]').forEach((card) => {
          const category = card.dataset.category;
          const visible = current === 'all' || category === current || category === 'all';
          card.style.display = visible ? '' : 'none';
        });
      });
    });
  });

  document.querySelectorAll('[data-ajax-form]').forEach((form) => {
    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      const submitButton = form.querySelector('button[type="submit"]');
      const originalLabel = submitButton ? submitButton.innerHTML : '';
      if (submitButton) {
        submitButton.disabled = true;
        submitButton.innerHTML = 'در حال ارسال...';
      }

      try {
        const response = await fetch(form.getAttribute('action') || window.location.href, {
          method: 'POST',
          body: new FormData(form),
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json',
          },
        });
        const data = await response.json();
        if (!response.ok || !data.ok) {
          const errorText = data.errors && data.errors.length ? data.errors.join(' | ') : (data.message || 'ارسال فرم انجام نشد.');
          createToast(errorText, 'error');
          return;
        }
        form.reset();
        createToast(data.message || 'فرم با موفقیت ثبت شد.', 'success');
        const parentDemoModal = form.closest('[data-demo-modal]');
        if (parentDemoModal) {
          setTimeout(() => {
            parentDemoModal.classList.remove('is-open');
            parentDemoModal.setAttribute('aria-hidden', 'true');
            document.body.classList.remove('demo-modal-open');
          }, 700);
        }
        if (data.redirect_to && form.dataset.redirectOnSuccess === 'true') {
          window.location.href = data.redirect_to;
        }
      } catch (error) {
        createToast('ارتباط با سرور برقرار نشد. لطفاً دوباره تلاش کنید.', 'error');
      } finally {
        if (submitButton) {
          submitButton.disabled = false;
          submitButton.innerHTML = originalLabel;
        }
      }
    });
  });



  const progress = document.querySelector('[data-reading-progress]');
  const articleBody = document.querySelector('[data-article-body]');
  if (progress && articleBody) {
    const updateReadingProgress = () => {
      const rect = articleBody.getBoundingClientRect();
      const total = articleBody.offsetHeight - window.innerHeight;
      const read = Math.min(Math.max(-rect.top, 0), Math.max(total, 1));
      progress.style.width = `${(read / Math.max(total, 1)) * 100}%`;
    };
    updateReadingProgress();
    window.addEventListener('scroll', updateReadingProgress, { passive: true });
    window.addEventListener('resize', updateReadingProgress);
  }

  document.querySelectorAll('[data-copy-url]').forEach((button) => {
    button.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(window.location.href);
        createToast('لینک مقاله کپی شد.', 'success');
      } catch (error) {
        createToast('کپی لینک انجام نشد. آدرس صفحه را دستی کپی کنید.', 'error');
      }
    });
  });

  document.querySelectorAll('.faq-item').forEach((item) => {
    item.addEventListener('toggle', () => {
      if (!item.open) return;
      document.querySelectorAll('.faq-item').forEach((other) => {
        if (other !== item) {
          other.open = false;
        }
      });
    });
  });

  // Stage 12: lightweight product tour tabs on the homepage.
  document.querySelectorAll('[data-home-tour-tabs]').forEach((tabs) => {
    const buttons = tabs.querySelectorAll('[data-tour]');
    const panelScope = tabs.closest('.product-tour-panel') || document;
    const panels = panelScope.querySelectorAll('[data-tour-panel]');

    const activateTour = (index) => {
      buttons.forEach((button) => {
        const active = button.dataset.tour === index;
        button.classList.toggle('is-active', active);
        button.setAttribute('aria-selected', active ? 'true' : 'false');
      });
      panels.forEach((panel) => {
        panel.classList.toggle('is-active', panel.dataset.tourPanel === index);
      });
    };

    buttons.forEach((button) => {
      button.setAttribute('role', 'tab');
      button.addEventListener('click', () => activateTour(button.dataset.tour));
    });
    panels.forEach((panel) => panel.setAttribute('role', 'tabpanel'));
  });

  // Stage 13: active sticky section navigation for the polished homepage.
  const homeSectionNav = document.querySelector('[data-home-section-nav]');
  const homeSectionLinks = document.querySelectorAll('[data-section-link]');
  const homeSections = document.querySelectorAll('[data-section-watch][id]');
  if (homeSectionNav && homeSectionLinks.length && homeSections.length) {
    const setActiveHomeSection = (id) => {
      homeSectionLinks.forEach((link) => {
        link.classList.toggle('is-active', link.dataset.sectionLink === id);
      });
    };

    const manualActivateFromScroll = () => {
      let currentId = homeSections[0].id;
      const offset = window.innerHeight * 0.34;
      homeSections.forEach((section) => {
        const rect = section.getBoundingClientRect();
        if (rect.top <= offset) {
          currentId = section.id;
        }
      });
      setActiveHomeSection(currentId);
    };

    if ('IntersectionObserver' in window) {
      const sectionObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setActiveHomeSection(entry.target.id);
          }
        });
      }, { rootMargin: '-28% 0px -58% 0px', threshold: 0.01 });
      homeSections.forEach((section) => sectionObserver.observe(section));
    }

    window.addEventListener('scroll', manualActivateFromScroll, { passive: true });
    manualActivateFromScroll();

    homeSectionLinks.forEach((link) => {
      link.addEventListener('click', () => {
        setActiveHomeSection(link.dataset.sectionLink);
      });
    });
  }

});

// Stage 18: feature page deep module tabs.
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-feature-suite-tabs]').forEach((tabs) => {
    const buttons = tabs.querySelectorAll('[data-feature-suite]');
    const scope = tabs.closest('.feature-suite-panel') || document;
    const panels = scope.querySelectorAll('[data-feature-suite-panel]');
    const activate = (id) => {
      buttons.forEach((button) => button.classList.toggle('is-active', button.dataset.featureSuite === id));
      panels.forEach((panel) => panel.classList.toggle('is-active', panel.dataset.featureSuitePanel === id));
    };
    buttons.forEach((button) => button.addEventListener('click', () => activate(button.dataset.featureSuite)));
  });
});


// Stage 32.4: Demo request modal.
document.addEventListener('DOMContentLoaded', () => {
  const modal = document.querySelector('[data-demo-modal]');
  if (!modal) return;
  const openButtons = document.querySelectorAll('[data-demo-open]');
  const closeButtons = modal.querySelectorAll('[data-demo-close]');
  const firstInput = modal.querySelector('input, select, textarea, button');

  const openDemoModal = (event) => {
    if (event) event.preventDefault();
    modal.classList.add('is-open');
    modal.setAttribute('aria-hidden', 'false');
    document.body.classList.add('demo-modal-open');
    setTimeout(() => firstInput && firstInput.focus(), 80);
  };

  const closeDemoModal = () => {
    modal.classList.remove('is-open');
    modal.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('demo-modal-open');
  };

  openButtons.forEach((button) => button.addEventListener('click', openDemoModal));
  closeButtons.forEach((button) => button.addEventListener('click', closeDemoModal));
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && modal.classList.contains('is-open')) {
      closeDemoModal();
    }
  });

  if (window.location.hash === '#demo-request') {
    openDemoModal();
  }
});
