const { SlashCommandBuilder, EmbedBuilder, ActionRowBuilder, StringSelectMenuBuilder, ComponentType } = require('discord.js');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('gestion_monetaire')
        .setDescription('Interface de gestion économique avec options pour membres et staff'),

    async execute(interaction) {
        // Vérifier les permissions pour les options staff
        const isStaff = interaction.member.permissions.has('MANAGE_GUILD') || 
                       interaction.member.roles.cache.some(role => 
                           [1410802014769643603, 1418246098442780692, 1418245630639476868].includes(role.id)
                       );
        const isAdmin = interaction.member.permissions.has('ADMINISTRATOR') || 
                       [300740726257139712].includes(interaction.user.id);

        // Options pour les membres
        const memberOptions = [
            {
                label: 'Budget',
                description: 'Voir le budget de votre pays',
                value: 'budget',
                emoji: '💰'
            },
            {
                label: 'Produit intérieur brut',
                description: 'Voir le PIB de votre pays',
                value: 'pib',
                emoji: '📊'
            },
            {
                label: 'Emprunt',
                description: 'Voir et gérer vos emprunts',
                value: 'emprunt',
                emoji: '🏦'
            }
        ];

        // Options pour le staff
        const staffOptions = [
            {
                label: 'Ajouter de l\'argent',
                description: '[STAFF] Ajouter de l\'argent (PIB/Budget) à un pays',
                value: 'add_money',
                emoji: '➕'
            },
            {
                label: 'Retirer de l\'argent',
                description: '[STAFF] Retirer de l\'argent (PIB/Budget) à un pays',
                value: 'remove_money',
                emoji: '➖'
            },
            {
                label: 'Réinitialiser l\'Économie',
                description: '[ADMIN] Réinitialiser l\'économie complète ou d\'un pays',
                value: 'reset_economy',
                emoji: '🔄'
            }
        ];

        // Menu déroulant pour les membres
        const memberSelect = new StringSelectMenuBuilder()
            .setCustomId('member_economy_select')
            .setPlaceholder('[MEMBRE] Choisi l\'option...')
            .addOptions(memberOptions);

        // Menu déroulant pour le staff (affiché seulement si l'utilisateur a les permissions)
        const staffSelect = new StringSelectMenuBuilder()
            .setCustomId('staff_economy_select')
            .setPlaceholder('[STAFF/ADMIN] Choisi l\'option...')
            .addOptions(staffOptions)
            .setDisabled(!isStaff); // Désactivé si pas staff

        const memberRow = new ActionRowBuilder().addComponents(memberSelect);
        const staffRow = new ActionRowBuilder().addComponents(staffSelect);

        // Embed principal avec le container
        const embed = new EmbedBuilder()
            .setTitle('<:PX_economie:1424378553235017911> Gestion Économique')
            .setDescription(
                '> ▪︎ Ci-dessous, vous avez deux menus déroulants avec différentes options présentes au sein de la commande pour la **Gestion Économique**. Vous pouvez voir à combien s\'élève votre budget, votre PIB, mais également des options que seuls les Staffs peuvent utiliser.\n' +
                '> \n' +
                '> ➢ `⠀𝐌𝐄𝐌𝐁𝐑𝐄𝐒 :⠀`\n' +
                '> ● **Budget**\n' +
                '> -# Permet de voir le budget de votre pays.\n' +
                '> ● **Produit intérieur brut**\n' +
                '> -# Permet de voir le PIB de votre pays.\n' +
                '> ● **Emprunt**\n' +
                '> -# Permet de voir les emprunts contractés, et de les gérer.\n' +
                '> \n' +
                '> ➢ `⠀𝐒𝐓𝐀𝐅𝐅𝐒 :⠀`\n' +
                '> ● **Ajouter de l\'argent**\n' +
                '> -# [STAFF] Permet d\'ajouter de l\'argent (PIB/Budget) à un pays tiers.\n' +
                '> ● **Retirer de l\'argent**\n' +
                '> -# [STAFF] Permet de retirer de l\'argent (PIB/Budget) à un pays tiers.\n' +
                '> ● **Réinitialiser l\'Économie**\n' +
                '> -# [ADMIN] Réinitialise l\'économie, avec une option pour réinitialise l\'économie d\'un pays précis.'
            )
            .setImage('https://cdn.discordapp.com/attachments/1412872314525192233/1435412669304672277/Code.png')
            .setThumbnail('https://cdn.discordapp.com/attachments/1412872314525192233/1435413286345642014/Icone_-_Pax_Ruinae_24.png')
            .setColor(0xefe7c5);

        await interaction.reply({
            embeds: [embed],
            components: [memberRow, staffRow],
            ephemeral: false
        });

        // Collecteur pour les interactions avec les menus
        const collector = interaction.channel.createMessageComponentCollector({
            componentType: ComponentType.StringSelect,
            time: 300000 // 5 minutes
        });

        collector.on('collect', async (selectInteraction) => {
            if (selectInteraction.user.id !== interaction.user.id) {
                await selectInteraction.reply({
                    content: 'Vous ne pouvez pas utiliser ce menu.',
                    ephemeral: true
                });
                return;
            }

            const selectedValue = selectInteraction.values[0];

            try {
                switch (selectedValue) {
                    case 'budget':
                        await this.handleBudget(selectInteraction);
                        break;
                    case 'pib':
                        await this.handlePIB(selectInteraction);
                        break;
                    case 'emprunt':
                        await this.handleEmprunt(selectInteraction);
                        break;
                    case 'add_money':
                        if (!isStaff) {
                            await selectInteraction.reply({
                                content: '❌ Vous n\'avez pas les permissions pour cette action.',
                                ephemeral: true
                            });
                            return;
                        }
                        await this.handleAddMoney(selectInteraction);
                        break;
                    case 'remove_money':
                        if (!isStaff) {
                            await selectInteraction.reply({
                                content: '❌ Vous n\'avez pas les permissions pour cette action.',
                                ephemeral: true
                            });
                            return;
                        }
                        await this.handleRemoveMoney(selectInteraction);
                        break;
                    case 'reset_economy':
                        if (!isAdmin) {
                            await selectInteraction.reply({
                                content: '❌ Vous devez être administrateur pour cette action.',
                                ephemeral: true
                            });
                            return;
                        }
                        await this.handleResetEconomy(selectInteraction);
                        break;
                }
            } catch (error) {
                console.error('Erreur lors du traitement de la sélection:', error);
                await selectInteraction.reply({
                    content: '❌ Une erreur est survenue lors du traitement de votre demande.',
                    ephemeral: true
                });
            }
        });

        collector.on('end', () => {
            // Désactiver les menus après expiration
            memberSelect.setDisabled(true);
            staffSelect.setDisabled(true);
            
            interaction.editReply({
                embeds: [embed],
                components: [
                    new ActionRowBuilder().addComponents(memberSelect),
                    new ActionRowBuilder().addComponents(staffSelect)
                ]
            }).catch(() => {});
        });
    },

    // Gestionnaires pour chaque option
    async handleBudget(interaction) {
        await interaction.reply({
            content: '💰 **Budget de votre pays**\n> Cette fonction afficherait le budget de votre pays.\n> *Intégration avec les commandes Python en cours...*',
            ephemeral: true
        });
    },

    async handlePIB(interaction) {
        await interaction.reply({
            content: '📊 **PIB de votre pays**\n> Cette fonction afficherait le PIB de votre pays.\n> *Intégration avec les commandes Python en cours...*',
            ephemeral: true
        });
    },

    async handleEmprunt(interaction) {
        await interaction.reply({
            content: '🏦 **Gestion des emprunts**\n> Cette fonction afficherait vos emprunts et permettrait de les gérer.\n> *Intégration avec les commandes Python en cours...*',
            ephemeral: true
        });
    },

    async handleAddMoney(interaction) {
        await interaction.reply({
            content: '➕ **[STAFF] Ajouter de l\'argent**\n> Cette fonction permettrait d\'ajouter de l\'argent à un pays.\n> *Intégration avec les commandes Python en cours...*',
            ephemeral: true
        });
    },

    async handleRemoveMoney(interaction) {
        await interaction.reply({
            content: '➖ **[STAFF] Retirer de l\'argent**\n> Cette fonction permettrait de retirer de l\'argent à un pays.\n> *Intégration avec les commandes Python en cours...*',
            ephemeral: true
        });
    },

    async handleResetEconomy(interaction) {
        await interaction.reply({
            content: '🔄 **[ADMIN] Réinitialiser l\'économie**\n> Cette fonction permettrait de réinitialiser l\'économie.\n> *Intégration avec les commandes Python en cours...*',
            ephemeral: true
        });
    }
};
