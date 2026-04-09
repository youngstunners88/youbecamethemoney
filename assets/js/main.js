        // Sand Particles
        const sandContainer = document.getElementById('sandParticles');
        for (let i = 0; i < 30; i++) {
            const grain = document.createElement('div');
            grain.className = 'sand-grain';
            grain.style.left = Math.random() * 100 + '%';
            grain.style.animationDelay = Math.random() * 10 + 's';
            grain.style.animationDuration = (8 + Math.random() * 6) + 's';
            sandContainer.appendChild(grain);
        }

        // Service Pillar Toggle
        function togglePillar(pillar) {
            const wasActive = pillar.classList.contains('active');
            document.querySelectorAll('.service-pillar').forEach(p => p.classList.remove('active'));
            if (!wasActive) pillar.classList.add('active');
        }

        // Scroll Animations
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => { if (entry.isIntersecting) entry.target.classList.add('visible'); });
        }, { threshold: 0.1 });
        document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));

        // Smooth Scroll
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                e.preventDefault();
                document.querySelector(this.getAttribute('href'))?.scrollIntoView({ behavior: 'smooth' });
            });
        });

        // Music Player
        const MusicPlayer = {
            widget: null,
            isPlaying: false,
            isReady: false,
            currentVolume: 70,
            isMuted: false,
            duration: 0,
            currentPosition: 0,
            trackInfo: null,

            elements: {
                iframe: document.getElementById('scWidget'),
                playBtn: document.getElementById('playBtn'),
                playIcon: document.getElementById('playIcon'),
                trackName: document.getElementById('trackName'),
                trackArtist: document.getElementById('trackArtist'),
                progressBar: document.getElementById('progressBar'),
                progressContainer: document.getElementById('progressContainer'),
                currentTime: document.getElementById('currentTime'),
                duration: document.getElementById('duration'),
                volumeBtn: document.getElementById('volumeBtn'),
                volumeIcon: document.getElementById('volumeIcon'),
                volumeSlider: document.getElementById('volumeSlider'),
                volumeFill: document.getElementById('volumeFill'),
                expandBtn: document.getElementById('expandBtn'),
                player: document.getElementById('musicPlayer'),
                errorMessage: document.getElementById('errorMessage')
            },

            init() {
                this.loadSCAPI().then(() => {
                    this.setupWidget();
                }).catch(err => {
                    console.error('Failed to load SoundCloud API:', err);
                    this.showError('Music player temporarily unavailable');
                    this.elements.trackArtist.textContent = 'Unavailable';
                });
                this.bindEvents();
            },

            loadSCAPI() {
                return new Promise((resolve, reject) => {
                    if (window.SC && window.SC.Widget) {
                        resolve();
                        return;
                    }
                    const script = document.createElement('script');
                    script.src = 'https://w.soundcloud.com/player/api.js';
                    script.async = true;
                    script.onload = () => resolve();
                    script.onerror = () => reject(new Error('Failed to load SoundCloud API'));
                    document.head.appendChild(script);
                });
            },

            setupWidget() {
                try {
                    this.widget = SC.Widget(this.elements.iframe);
                    
                    this.widget.bind(SC.Widget.Events.READY, () => {
                        this.isReady = true;
                        this.widget.getDuration((duration) => {
                            this.duration = duration;
                            this.elements.duration.textContent = this.formatTime(duration);
                        });
                        this.widget.getCurrentSound((sound) => {
                            if (sound) {
                                this.trackInfo = sound;
                                this.elements.trackName.textContent = sound.title || 'You Became The Money';
                                this.elements.trackArtist.textContent = sound.user ? sound.user.username : 'Daniel Garcia';
                            } else {
                                this.elements.trackArtist.textContent = 'Daniel Garcia';
                            }
                        });
                        this.widget.setVolume(this.currentVolume);
                        this.startProgressTracking();
                    });

                    this.widget.bind(SC.Widget.Events.PLAY, () => {
                        this.isPlaying = true;
                        this.updatePlayButton();
                    });

                    this.widget.bind(SC.Widget.Events.PAUSE, () => {
                        this.isPlaying = false;
                        this.updatePlayButton();
                    });

                    this.widget.bind(SC.Widget.Events.FINISH, () => {
                        this.isPlaying = false;
                        this.updatePlayButton();
                        this.elements.progressBar.style.width = '0%';
                        this.elements.currentTime.textContent = '0:00';
                    });

                    this.widget.bind(SC.Widget.Events.ERROR, (error) => {
                        console.error('SoundCloud Widget Error:', error);
                        this.showError('Failed to load audio. Please try again.');
                        this.isPlaying = false;
                        this.updatePlayButton();
                    });

                } catch (error) {
                    console.error('Error setting up widget:', error);
                    this.elements.trackArtist.textContent = 'Unavailable';
                }
            },

            bindEvents() {
                this.elements.playBtn.addEventListener('click', () => this.togglePlay());

                this.elements.progressContainer.addEventListener('click', (e) => {
                    if (!this.isReady) return;
                    const rect = this.elements.progressContainer.getBoundingClientRect();
                    const percent = (e.clientX - rect.left) / rect.width;
                    const seekTime = percent * this.duration;
                    this.widget.seekTo(seekTime);
                });

                this.elements.volumeSlider.addEventListener('click', (e) => {
                    if (!this.isReady) return;
                    const rect = this.elements.volumeSlider.getBoundingClientRect();
                    const percent = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
                    this.setVolume(percent * 100);
                });

                this.elements.volumeBtn.addEventListener('click', () => this.toggleMute());

                this.elements.expandBtn.addEventListener('click', () => {
                    this.elements.player.classList.toggle('expanded');
                });
            },

            togglePlay() {
                if (!this.isReady) {
                    this.showError('Player is loading, please wait...');
                    return;
                }
                this.widget.toggle();
            },

            updatePlayButton() {
                if (this.isPlaying) {
                    this.elements.playBtn.classList.add('playing');
                    this.elements.playIcon.className = 'fas fa-pause';
                } else {
                    this.elements.playBtn.classList.remove('playing');
                    this.elements.playIcon.className = 'fas fa-play';
                }
            },

            setVolume(value) {
                this.currentVolume = value;
                this.widget.setVolume(value);
                this.elements.volumeFill.style.width = value + '%';
                if (value === 0) {
                    this.elements.volumeIcon.className = 'fas fa-volume-off';
                } else if (value < 50) {
                    this.elements.volumeIcon.className = 'fas fa-volume-down';
                } else {
                    this.elements.volumeIcon.className = 'fas fa-volume-up';
                }
                this.isMuted = value === 0;
            },

            toggleMute() {
                if (this.isMuted) {
                    this.setVolume(70);
                } else {
                    this.setVolume(0);
                }
            },

            startProgressTracking() {
                const updateProgress = () => {
                    if (this.isPlaying && this.isReady) {
                        this.widget.getPosition((position) => {
                            this.currentPosition = position;
                            const percent = this.duration > 0 ? (position / this.duration) * 100 : 0;
                            this.elements.progressBar.style.width = percent + '%';
                            this.elements.currentTime.textContent = this.formatTime(position);
                        });
                    }
                    requestAnimationFrame(updateProgress);
                };
                updateProgress();
            },

            formatTime(ms) {
                const totalSeconds = Math.floor(ms / 1000);
                const minutes = Math.floor(totalSeconds / 60);
                const seconds = totalSeconds % 60;
                return `${minutes}:${seconds.toString().padStart(2, '0')}`;
            },

            showError(message) {
                this.elements.errorMessage.textContent = message;
                this.elements.errorMessage.classList.add('show');
                setTimeout(() => {
                    this.elements.errorMessage.classList.remove('show');
                }, 4000);
            }
        };

        MusicPlayer.init();
