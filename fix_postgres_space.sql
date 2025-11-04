-- Script de nettoyage d'urgence PostgreSQL - Problème d'espace disque
-- ERREUR: "No space left on device" dans pg_wal/xlogtemp.29

-- 1. Supprimer les anciennes données de backup si elles existent
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'json_backups') THEN
        -- Supprimer les backups de plus de 30 jours
        DELETE FROM json_backups 
        WHERE backup_date < NOW() - INTERVAL '30 days';
        
        -- Supprimer les gros fichiers (>1MB) sauf les plus récents
        DELETE FROM json_backups 
        WHERE LENGTH(content) > 1000000 
        AND backup_date < (
            SELECT MAX(backup_date) - INTERVAL '7 days' 
            FROM json_backups
        );
        
        RAISE NOTICE 'Nettoyage json_backups terminé';
    END IF;
END $$;

-- 2. Nettoyer les logs système
DO $$
BEGIN
    -- Nettoyer pg_stat_statements si présent
    IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements') THEN
        SELECT pg_stat_statements_reset();
        RAISE NOTICE 'pg_stat_statements nettoyé';
    END IF;
END $$;

-- 3. Vacuum complet pour récupérer l'espace
VACUUM FULL;

-- 4. Reindex pour optimiser
REINDEX DATABASE railway;

-- 5. Analyser les statistiques
ANALYZE;

-- 6. Afficher l'espace récupéré
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size('"'||schemaname||'"."'||tablename||'"')) as taille
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size('"'||schemaname||'"."'||tablename||'"') DESC;

-- Afficher l'espace total utilisé
SELECT pg_size_pretty(pg_database_size(current_database())) as taille_base;