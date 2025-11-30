import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { dashboardService, VesselStatus } from '../api/services';

export default function FleetScreen({ navigation }: any) {
    const [vessels, setVessels] = useState<VesselStatus[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            const data = await dashboardService.getFleetStatus();
            setVessels(data.vessels);
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    const getStatusColor = (status: string) => {
        switch (status?.toLowerCase()) {
            case 'critical': return '#d32f2f';
            case 'warning': return '#ed6c02';
            case 'good': return '#2e7d32';
            default: return '#666';
        }
    };

    const renderItem = ({ item }: { item: VesselStatus }) => (
        <TouchableOpacity
            style={styles.card}
            onPress={() => navigation.navigate('VesselDetails', { vesselId: item.id })}
        >
            <View style={styles.cardHeader}>
                <Text style={styles.vesselName}>{item.name}</Text>
                <View style={[styles.badge, { backgroundColor: getStatusColor(item.compliance_status) }]}>
                    <Text style={styles.badgeText}>{item.compliance_status}</Text>
                </View>
            </View>
            <View style={styles.row}>
                <Text style={styles.label}>Bioincrustação:</Text>
                <Text style={styles.value}>{item.fouling_mm.toFixed(2)} mm</Text>
            </View>
            <View style={styles.row}>
                <Text style={styles.label}>Rugosidade:</Text>
                <Text style={styles.value}>{item.roughness_um.toFixed(0)} µm</Text>
            </View>
        </TouchableOpacity>
    );

    return (
        <SafeAreaView style={styles.container}>
            <View style={styles.header}>
                <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
                    <Text style={styles.backText}>← Voltar</Text>
                </TouchableOpacity>
                <Text style={styles.title}>Frota</Text>
                <View style={{ width: 50 }} />
            </View>

            {loading ? (
                <ActivityIndicator size="large" color="#0070f3" style={{ marginTop: 20 }} />
            ) : (
                <FlatList
                    data={vessels}
                    renderItem={renderItem}
                    keyExtractor={item => item.id}
                    contentContainerStyle={styles.list}
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
        marginBottom: 12,
    },
    vesselName: { fontSize: 16, fontWeight: 'bold' },
    badge: { paddingHorizontal: 8, paddingVertical: 4, borderRadius: 12 },
    badgeText: { color: '#fff', fontSize: 10, fontWeight: 'bold', textTransform: 'uppercase' },
    row: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 4 },
    label: { color: '#666' },
    value: { fontWeight: '600' },
});
