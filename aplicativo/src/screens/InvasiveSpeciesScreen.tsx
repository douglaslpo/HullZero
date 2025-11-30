import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { invasiveSpeciesService } from '../api/services';

export default function InvasiveSpeciesScreen({ navigation }: any) {
    const [species, setSpecies] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            const data = await invasiveSpeciesService.list();
            setSpecies(data);
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    const getRiskColor = (level: string) => {
        switch (level?.toLowerCase()) {
            case 'alto': return '#d32f2f';
            case 'médio': return '#ed6c02';
            case 'baixo': return '#2e7d32';
            default: return '#666';
        }
    };

    const renderItem = ({ item }: { item: any }) => (
        <View style={styles.card}>
            <View style={styles.cardHeader}>
                <Text style={styles.speciesName}>{item.name}</Text>
                <View style={[styles.badge, { backgroundColor: getRiskColor(item.risk_level) }]}>
                    <Text style={styles.badgeText}>{item.risk_level}</Text>
                </View>
            </View>
            <Text style={styles.description}>{item.description}</Text>
            <Text style={styles.regions}>Regiões: {item.regions?.join(', ')}</Text>
        </View>
    );

    return (
        <SafeAreaView style={styles.container}>
            <View style={styles.header}>
                <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
                    <Text style={styles.backText}>← Voltar</Text>
                </TouchableOpacity>
                <Text style={styles.title}>Espécies Invasoras</Text>
                <View style={{ width: 50 }} />
            </View>

            {loading ? (
                <ActivityIndicator size="large" color="#0070f3" style={{ marginTop: 20 }} />
            ) : (
                <FlatList
                    data={species}
                    renderItem={renderItem}
                    keyExtractor={(item, index) => index.toString()}
                    contentContainerStyle={styles.list}
                    ListEmptyComponent={<Text style={styles.emptyText}>Nenhuma espécie encontrada.</Text>}
                />
            )}
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f0f2f5',
    },
    header: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: 16,
        backgroundColor: '#fff',
        borderBottomWidth: 1,
        borderBottomColor: '#eee',
    },
    backButton: { padding: 8 },
    backText: { color: '#0070f3', fontSize: 16 },
    title: { fontSize: 18, fontWeight: 'bold' },
    list: { padding: 16 },
    card: {
        backgroundColor: '#fff',
        padding: 16,
        borderRadius: 12,
        marginBottom: 12,
        elevation: 2,
    },
    cardHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 8,
    },
    speciesName: { fontSize: 16, fontWeight: 'bold', color: '#333' },
    badge: { paddingHorizontal: 8, paddingVertical: 4, borderRadius: 12 },
    badgeText: { color: '#fff', fontSize: 10, fontWeight: 'bold', textTransform: 'uppercase' },
    description: { color: '#666', marginBottom: 8 },
    regions: { fontSize: 12, color: '#888', fontStyle: 'italic' },
    emptyText: { textAlign: 'center', marginTop: 20, color: '#666' },
});
