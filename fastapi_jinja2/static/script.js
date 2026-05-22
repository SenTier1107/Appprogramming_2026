// 곡 제목 클릭 시 작곡가+제목을 클립보드에 복사
document.querySelectorAll('.piece-item a').forEach(link => {
    link.addEventListener('click', () => {
        const title    = link.querySelector('strong')?.textContent ?? '';
        const composer = link.querySelector('.composer')?.textContent ?? '';
        navigator.clipboard.writeText(`${title} ${composer}`.trim()).catch(() => {});
    });
});
