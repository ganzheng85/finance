// Translation dictionary for English and Chinese
const translations = {
    en: {
        // Header
        'app.title': 'Stock Analysis Dashboard',
        'app.subtitle': 'Comprehensive Financial Analysis Platform',

        // Language selector
        'lang.english': 'English',
        'lang.chinese': '中文',

        // Disclaimer
        'disclaimer.title': 'Important Disclaimer',
        'disclaimer.educational.title': 'Educational Purpose Only:',
        'disclaimer.educational.text': 'This tool is designed for educational and informational purposes only. It is not intended to provide investment advice or recommendations.',
        'disclaimer.notPersonalized.title': 'Not Personalized Advice:',
        'disclaimer.notPersonalized.text': 'The analysis and reports generated are based on publicly available data and standardized algorithms. They do not take into account your personal financial situation, investment objectives, risk tolerance, or specific needs.',
        'disclaimer.noGuarantee.title': 'No Performance Guarantee:',
        'disclaimer.noGuarantee.text': 'Past performance is not indicative of future results. No guarantee or representation is made that any analysis, strategy, or recommendation will be profitable or will not result in losses.',
        'disclaimer.responsibility.title': 'User Responsibility:',
        'disclaimer.responsibility.text': 'You are solely responsible for your own investment decisions. Always conduct your own research and consult with a licensed financial advisor before making any investment decisions.',
        'disclaimer.risks.title': 'Trading Risks:',
        'disclaimer.risks.text': 'Trading stocks and securities involves substantial risk of loss. You should only invest money you can afford to lose. Market conditions can change rapidly, and past trends may not continue.',
        'disclaimer.footer': 'By using this tool, you acknowledge and agree to these terms.',

        // Tabs
        'tab.company': 'Company Analysis',
        'tab.sector': 'Sector Rotation',
        'tab.contact': 'Contact Author',

        // Company Analysis
        'company.title': 'Generate Analysis Reports',
        'company.ticker.label': 'Stock Ticker Symbol',
        'company.ticker.placeholder': 'e.g., AAPL, TSLA, MSFT',
        'company.ticker.help': 'Enter a valid stock ticker symbol',
        'company.reportType.label': 'Select Report Types',
        'company.reportLanguage.label': 'Report Language:',
        'company.reportLanguage.hint': '(Change using language selector above)',
        'company.reportLanguage.english': 'English',
        'company.reportLanguage.chinese': 'Chinese (中文)',
        'company.fundamental.title': 'Fundamental Research',
        'company.fundamental.desc': 'Company data, competitive metrics, financial indicators',
        'company.fundamental.sample': '📄 View Sample Report (MSFT)',
        'company.technical.title': 'Technical Analysis',
        'company.technical.desc': 'Indicators, patterns, price trends, data summaries',
        'company.button': 'Generate Reports',
        'company.button.loading': 'Analyzing...',
        'company.results.title': 'Analysis Results',

        // Sector Analysis
        'sector.title': 'Sector Rotation Analysis',
        'sector.subtitle': 'Track institutional money flow across 13 market sectors (11 S&P sectors + Semiconductors + Magnificent 7)',
        'sector.button': 'Generate Sector Analysis',
        'sector.help': 'Analyzes 13 sectors by momentum, relative strength, and rotation patterns',
        'sector.loading': 'Analyzing sector rotation... This may take 30-60 seconds...',
        'sector.rankings.title': 'Sector Rankings',
        'sector.rankings.rank': 'Rank',
        'sector.rankings.sector': 'Sector',
        'sector.rankings.score': 'Score',
        'sector.rankings.rs': 'RS (20d)',
        'sector.rankings.momentum': 'Momentum',
        'sector.rankings.signal': 'Signal',
        'sector.rotation.title': 'Rotation Map',
        'sector.rotation.leading': 'Leading (Strong + Accelerating)',
        'sector.rotation.weakening': 'Weakening (Strong + Decelerating)',
        'sector.rotation.lagging': 'Lagging (Weak + Decelerating)',
        'sector.rotation.improving': 'Improving (Weak + Accelerating)',
        'sector.rotation.none': 'None',
        'sector.portfolio.title': 'Portfolio Recommendation',
        'sector.portfolio.top5': 'Recommended Allocation (Top 5):',
        'sector.portfolio.bottom3': 'Avoid (Bottom 3):',
        'sector.viewReport': 'View Full Report',

        // Contact
        'contact.title': 'Contact Author',
        'contact.subtitle': 'Have questions or feedback? Send me a message and I\'ll get back to you!',
        'contact.name.label': 'Your Name',
        'contact.name.placeholder': 'John Doe',
        'contact.email.label': 'Your Email Address',
        'contact.email.placeholder': 'john@example.com',
        'contact.email.help': 'I\'ll use this to respond to your message',
        'contact.subject.label': 'Subject',
        'contact.subject.placeholder': 'Question about technical analysis',
        'contact.message.label': 'Your Message',
        'contact.message.placeholder': 'Type your message here...',
        'contact.message.help': 'Please provide as much detail as possible',
        'contact.button': 'Send Message',
        'contact.button.loading': 'Sending...',
        'contact.success.title': 'Message Sent!',
        'contact.success.text': 'Thank you for your message. I will get back to you soon!',

        // Footer
        'footer.copyright': '© 2026 Stock Analysis Dashboard v1.0'
    },

    zh: {
        // Header
        'app.title': '股票分析仪表板',
        'app.subtitle': '综合金融分析平台',

        // Language selector
        'lang.english': 'English',
        'lang.chinese': '中文',

        // Disclaimer
        'disclaimer.title': '重要免责声明',
        'disclaimer.educational.title': '仅供教育目的：',
        'disclaimer.educational.text': '本工具仅用于教育和信息目的，不提供投资建议或推荐。',
        'disclaimer.notPersonalized.title': '非个性化建议：',
        'disclaimer.notPersonalized.text': '生成的分析和报告基于公开数据和标准化算法。它们不考虑您的个人财务状况、投资目标、风险承受能力或特定需求。',
        'disclaimer.noGuarantee.title': '无业绩保证：',
        'disclaimer.noGuarantee.text': '过往表现不代表未来结果。不保证任何分析、策略或推荐会盈利或不会造成损失。',
        'disclaimer.responsibility.title': '用户责任：',
        'disclaimer.responsibility.text': '您对自己的投资决策负全部责任。在做出任何投资决策之前，请务必进行自己的研究并咨询持牌财务顾问。',
        'disclaimer.risks.title': '交易风险：',
        'disclaimer.risks.text': '交易股票和证券存在重大损失风险。您应该只投资您能承受损失的资金。市场状况可能迅速变化，过去的趋势可能不会持续。',
        'disclaimer.footer': '使用本工具即表示您承认并同意这些条款。',

        // Tabs
        'tab.company': '公司分析',
        'tab.sector': '板块轮动',
        'tab.contact': '联系作者',

        // Company Analysis
        'company.title': '生成分析报告',
        'company.ticker.label': '股票代码',
        'company.ticker.placeholder': '例如：AAPL, TSLA, MSFT',
        'company.ticker.help': '请输入有效的股票代码',
        'company.reportType.label': '选择报告类型',
        'company.reportLanguage.label': '报告语言：',
        'company.reportLanguage.hint': '（使用上方语言选择器更改）',
        'company.reportLanguage.english': 'English',
        'company.reportLanguage.chinese': '中文',
        'company.fundamental.title': '基本面研究',
        'company.fundamental.desc': '公司数据、竞争指标、财务指标',
        'company.fundamental.sample': '📄 查看示例报告 (MSFT)',
        'company.technical.title': '技术分析',
        'company.technical.desc': '指标、形态、价格趋势、数据摘要',
        'company.button': '生成报告',
        'company.button.loading': '分析中...',
        'company.results.title': '分析结果',

        // Sector Analysis
        'sector.title': '板块轮动分析',
        'sector.subtitle': '跟踪13个市场板块的机构资金流向（11个标普板块 + 半导体 + 科技七巨头）',
        'sector.button': '生成板块分析',
        'sector.help': '通过动量、相对强度和轮动模式分析13个板块',
        'sector.loading': '正在分析板块轮动... 可能需要30-60秒...',
        'sector.rankings.title': '板块排名',
        'sector.rankings.rank': '排名',
        'sector.rankings.sector': '板块',
        'sector.rankings.score': '评分',
        'sector.rankings.rs': '相对强度 (20天)',
        'sector.rankings.momentum': '动量',
        'sector.rankings.signal': '信号',
        'sector.rotation.title': '轮动图',
        'sector.rotation.leading': '领先（强势 + 加速）',
        'sector.rotation.weakening': '减弱（强势 + 减速）',
        'sector.rotation.lagging': '落后（弱势 + 减速）',
        'sector.rotation.improving': '改善（弱势 + 加速）',
        'sector.rotation.none': '无',
        'sector.portfolio.title': '投资组合建议',
        'sector.portfolio.top5': '推荐配置（前5名）：',
        'sector.portfolio.bottom3': '避免配置（后3名）：',
        'sector.viewReport': '查看完整报告',

        // Contact
        'contact.title': '联系作者',
        'contact.subtitle': '有问题或反馈？给我发消息，我会尽快回复您！',
        'contact.name.label': '您的姓名',
        'contact.name.placeholder': '张三',
        'contact.email.label': '您的电子邮件地址',
        'contact.email.placeholder': 'zhangsan@example.com',
        'contact.email.help': '我将使用此邮箱回复您的消息',
        'contact.subject.label': '主题',
        'contact.subject.placeholder': '关于技术分析的问题',
        'contact.message.label': '您的留言',
        'contact.message.placeholder': '在此输入您的消息...',
        'contact.message.help': '请尽可能详细地说明',
        'contact.button': '发送消息',
        'contact.button.loading': '发送中...',
        'contact.success.title': '消息已发送！',
        'contact.success.text': '感谢您的消息。我会尽快回复您！',

        // Footer
        'footer.copyright': '© 2026 股票分析仪表板 v1.0'
    }
};

// Language management
let currentLanguage = localStorage.getItem('language') || 'en';

// Expose to window for access from other scripts
window.currentLanguage = currentLanguage;

function setLanguage(lang) {
    currentLanguage = lang;
    window.currentLanguage = lang;  // Update global reference
    localStorage.setItem('language', lang);
    updatePageLanguage();
    updateLanguageButtons();
}

function updatePageLanguage() {
    // Update all elements with data-i18n attribute
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        if (translations[currentLanguage][key]) {
            element.textContent = translations[currentLanguage][key];
        }
    });

    // Update elements with data-i18n-placeholder attribute
    document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
        const key = element.getAttribute('data-i18n-placeholder');
        if (translations[currentLanguage][key]) {
            element.placeholder = translations[currentLanguage][key];
        }
    });

    // Update report language display
    const reportLangDisplay = document.getElementById('report-language-display');
    if (reportLangDisplay) {
        const langKey = currentLanguage === 'zh' ? 'company.reportLanguage.chinese' : 'company.reportLanguage.english';
        reportLangDisplay.textContent = translations[currentLanguage][langKey];
    }

    // Update HTML lang attribute
    document.documentElement.lang = currentLanguage;
}

function updateLanguageButtons() {
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-lang="${currentLanguage}"]`)?.classList.add('active');
}

// Initialize language on page load
document.addEventListener('DOMContentLoaded', () => {
    updatePageLanguage();
    updateLanguageButtons();
});
