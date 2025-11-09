// Sample data for demo purposes
const messages = [
    {
        id: 1,
        platform: 'whatsapp',
        from: '+1 234 567 890',
        name: 'John Smith',
        preview: 'Hi there! Just wanted to check if you received my last message about the project deadline?',
        body: 'Hi there! Just wanted to check if you received my last message about the project deadline? We need to finalize everything by Friday.',
        received: '5 min ago',
        status: 'unread',
        starred: false,
        avatar: 'http://static.photos/people/200x200/1'
    },
    {
        id: 2,
        platform: 'gmail',
        from: 'client@example.com',
        name: 'Sarah Johnson',
        preview: 'Project Proposal Review - Need your feedback by EOD',
        body: 'Hello,\n\nAttached is the project proposal we discussed last week. Please review and provide your feedback by end of day today.\n\nBest regards,\nSarah',
        received: '1 hour ago',
        status: 'read',
        starred: true,
        avatar: 'http://static.photos/people/200x200/2'
    },
    {
        id: 3,
        platform: 'outlook',
        from: 'manager@company.com',
        name: 'Michael Brown',
        preview: 'Team Meeting Reminder: Tomorrow at 10 AM',
        body: 'Hello Team,\n\nThis is a reminder about our quarterly planning meeting tomorrow at 10 AM in Conference Room B. Please bring your department reports.\n\nRegards,\nMichael',
        received: '3 hours ago',
        status: 'read',
        starred: false,
        avatar: 'http://static.photos/people/200x200/3'
    },
    {
        id: 4,
        platform: 'teams',
        from: 'teams@company.org',
        name: 'Design Team',
        preview: 'New comments on the wireframes in Design Channel',
        body: 'The team has left several comments on the latest wireframes. Please review and respond to the feedback when you have a chance.',
        received: 'Yesterday',
        status: 'read',
        starred: false,
        avatar: 'http://static.photos/people/200x200/4'
    },
    {
        id: 5,
        platform: 'whatsapp',
        from: '+44 7654 321098',
        name: 'David Wilson',
        preview: 'Are we still on for lunch tomorrow?',
        body: 'Hey! Just checking if we\'re still meeting for lunch tomorrow at that Italian place? Let me know if the time still works for you.',
        received: 'Yesterday',
        status: 'delivered',
        starred: false,
        avatar: 'http://static.photos/people/200x200/5'
    }
];

// DOM Elements
const messagesTable = document.getElementById('messages-table');
const tabButtons = document.querySelectorAll('.tab-btn');
const filterButtons = document.querySelectorAll('.filter-btn');
const messageModal = document.getElementById('message-modal');
const modalTitle = document.getElementById('modal-title');
const modalContent = document.getElementById('modal-content');
const closeModal = document.getElementById('close-modal');
const quickActions = document.getElementById('quick-actions');

// Render messages table
function renderMessages(filter = 'all', statusFilter = null) {
    messagesTable.innerHTML = '';
    
    const filteredMessages = messages.filter(msg => {
        const platformMatch = filter === 'all' || msg.platform === filter;
        const statusMatch = !statusFilter || msg.status === statusFilter;
        return platformMatch && statusMatch;
    });
    
    filteredMessages.forEach(message => {
        const row = document.createElement('tr');
        row.className = `message-row ${message.status === 'unread' ? 'unread' : ''}`;
        row.dataset.id = message.id;
        
        row.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap">
                <span class="platform-badge platform-${message.platform}">
                    <i data-feather="${getPlatformIcon(message.platform)}" class="mr-1"></i>
                    ${message.platform.charAt(0).toUpperCase() + message.platform.slice(1)}
                </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                    <div class="flex-shrink-0 h-10 w-10">
                        <img class="h-10 w-10 rounded-full" src="${message.avatar}" alt="">
                    </div>
                    <div class="ml-4">
                        <div class="text-sm font-medium text-gray-900">${message.name}</div>
                        <div class="text-sm text-gray-500">${message.from}</div>
                    </div>
                </div>
            </td>
            <td class="px-6 py-4">
                <div class="text-sm font-medium text-gray-900">${message.preview}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-500">${message.received}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <span class="status-indicator status-${message.status}"></span>
                <span class="text-sm text-gray-500 capitalize">${message.status}</span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button class="view-btn text-indigo-600 hover:text-indigo-900 mr-3">View</button>
                <button class="action-btn text-gray-600 hover:text-gray-900">
                    <i data-feather="more-vertical"></i>
                </button>
            </td>
        `;
        
        messagesTable.appendChild(row);
    });
    
    feather.replace();
    
    // Add event listeners to view buttons
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const messageId = e.target.closest('tr').dataset.id;
            showMessageModal(messageId);
        });
    });
}

function getPlatformIcon(platform) {
    const icons = {
        whatsapp: 'message-circle',
        gmail: 'mail',
        outlook: 'inbox',
        teams: 'users'
    };
    return icons[platform] || 'message-square';
}

function showMessageModal(messageId) {
    const message = messages.find(msg => msg.id == messageId);
    if (!message) return;
    
    modalTitle.textContent = `Message from ${message.name} (${message.from})`;
    modalContent.innerHTML = `
        <div class="bg-gray-50 p-4 rounded-lg">
            <div class="flex items-start">
                <img class="h-12 w-12 rounded-full mr-4" src="${message.avatar}" alt="${message.name}">
                <div>
                    <h4 class="font-medium text-gray-900">${message.name}</h4>
                    <p class="text-sm text-gray-500">${message.from}</p>
                    <p class="text-sm text-gray-500 mt-1">${message.received}</p>
                </div>
            </div>
            <div class="mt-4 whitespace-pre-line">${message.body}</div>
        </div>
    `;
    
    // Update quick actions based on platform
    updateQuickActions(message.platform);
    
    messageModal.classList.remove('hidden');
}

function updateQuickActions(platform) {
    // Clear existing actions
    quickActions.innerHTML = '';
    
    // Common actions
    const actions = [
        { icon: 'corner-up-left', text: 'Reply', class: 'bg-indigo-100 text-indigo-700 hover:bg-indigo-200' },
        { icon: 'corner-up-right', text: 'Forward', class: 'bg-blue-100 text-blue-700 hover:bg-blue-200' }
    ];
    
    // Platform-specific actions
    if (platform === 'whatsapp') {
        actions.push(
            { icon: 'clock', text: 'Schedule Reply', class: 'bg-purple-100 text-purple-700 hover:bg-purple-200' },
            { icon: 'phone', text: 'Voice Call', class: 'bg-green-100 text-green-700 hover:bg-green-200' }
        );
    } else if (platform === 'gmail' || platform === 'outlook') {
        actions.push(
            { icon: 'file-text', text: 'Use Template', class: 'bg-green-100 text-green-700 hover:bg-green-200' },
            { icon: 'archive', text: 'Archive', class: 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200' }
        );
    } else if (platform === 'teams') {
        actions.push(
            { icon: 'video', text: 'Start Meeting', class: 'bg-purple-100 text-purple-700 hover:bg-purple-200' },
            { icon: 'message-square', text: 'Group Reply', class: 'bg-green-100 text-green-700 hover:bg-green-200' }
        );
    }
    
    // Create action buttons
    const actionsContainer = document.createElement('div');
    actionsContainer.className = 'flex flex-wrap gap-2';
    
    actions.forEach(action => {
        const button = document.createElement('button');
        button.className = `quick-action-btn flex items-center px-4 py-2 rounded-lg ${action.class}`;
        button.innerHTML = `<i data-feather="${action.icon}" class="mr-2"></i>${action.text}`;
        actionsContainer.appendChild(button);
    });
    
    quickActions.appendChild(actionsContainer);
    feather.replace();
}

// Event Listeners
tabButtons.forEach(button => {
    button.addEventListener('click', () => {
        tabButtons.forEach(btn => btn.classList.remove('active', 'text-indigo-600'));
        button.classList.add('active', 'text-indigo-600');
        renderMessages(button.dataset.tab);
    });
});

filterButtons.forEach(button => {
    button.addEventListener('click', () => {
        const filter = button.dataset.filter;
        renderMessages(document.querySelector('.tab-btn.active').dataset.tab, filter === 'unread' ? 'unread' : null);
    });
});

closeModal.addEventListener('click', () => {
    messageModal.classList.add('hidden');
});

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    renderMessages();
});