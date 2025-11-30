import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, RefreshControl, ActivityIndicator } from 'react-native';
import { useAuth } from '../contexts/AuthContext';
import { SafeAreaView } from 'react-native-safe-area-context';
import { dashboardService, DashboardKPIs, FleetStatus, VesselStatus } from '../api/services';
import KPICard from '../components/KPICard';

export default function DashboardScreen({ navigation }: any) {
    const { signOut } = useAuth();
    const [kpis, setKpis] = useState<DashboardKPIs | null>(null);
    const [fleet, setFleet] = useState<VesselStatus[]>([]);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);

    const fetchData = async () => {
        try {
            const [kpisData, fleetData] = await Promise.all([
                dashboardService.getKPIs(),
                dashboardService.getFleetStatus()
            ]);
            setKpis(kpisData);
            setFleet(fleetData.vessels);
        } catch (error) {
            console.error('Erro ao buscar dados:', error);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const onRefresh = () => {
        setRefreshing(true);
        fetchData();
    };

    const getStatusColor = (status: string) => {
        switch (status.toLowerCase()) {
            case 'critical': return '#d32f2f';
            case 'warning': return '#ed6c02';
            case 'good': return '#2e7d32';
            default: return '#666';
        }
    };

    return (
        <SafeAreaView style={styles.container}>
            <View style={styles.header}>
                <Text style={styles.title}>HullZero</Text>
                <TouchableOpacity onPress={signOut} style={styles.logoutButton}>
                    <Text style={styles.logoutText}>Sair</Text>
                </TouchableOpacity>
            </View>

            <ScrollView
                contentContainerStyle={styles.content}
                refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
            >
                {loading ? (
                    <ActivityIndicator size="large" color="#0070f3" style={{ marginTop: 20 }} />
                ) : (
                    <>
                        <Text style={styles.sectionTitle}>Menu Rápido</Text>
                        <View style={styles.menuContainer}>
                            <TouchableOpacity style={styles.menuButton} onPress={() => navigation.navigate('Fleet')}>
                                <Text style={styles.menuButtonText}>🚢 Frota</Text>
                            </TouchableOpacity>
                            <TouchableOpacity style={styles.menuButton} onPress={() => navigation.navigate('Compliance')}>
                                <Text style={styles.menuButtonText}>✅ Conformidade</Text>
                            </TouchableOpacity>
                            <TouchableOpacity style={styles.menuButton} onPress={() => navigation.navigate('InvasiveSpecies')}>
                                <Text style={styles.menuButtonText}>🦀 Espécies</Text>
                            </TouchableOpacity>
                        </View>

                        <Text style={styles.sectionTitle}>Resumo da Frota</Text>
                        <View style={styles.kpiContainer}>
                            <KPICard
                                label="Economia"
                                value={`R$ ${(kpis?.accumulated_economy_brl || 0).toLocaleString('pt-BR', { notation: 'compact' })}`}
                                color="#2e7d32"
                            />
                            <KPICard
                                label="Redução CO₂"
                                value={`${(kpis?.co2_reduction_tonnes || 0).toFixed(0)} t`}
                                color="#009688"
                            />
                            <KPICard
                                label="Conformidade"
                                value={`${(kpis?.compliance_rate_percent || 0).toFixed(0)}%`}
                                color="#ed6c02"
                            />
                            <KPICard
                                label="Embarcações"
                                value={kpis?.monitored_vessels || 0}
                                color="#0288d1"
                            />
                        </View>

                        <Text style={styles.sectionTitle}>Status das Embarcações</Text>
                        {fleet.map((vessel) => (
                            <TouchableOpacity
                                key={vessel.id}
                                style={styles.vesselCard}
                                onPress={() => navigation.navigate('VesselDetails', { vesselId: vessel.id })}
                            >
                                <View style={styles.vesselHeader}>
                                    <Text style={styles.vesselName}>{vessel.name}</Text>
                                    <View style={[styles.statusBadge, { backgroundColor: getStatusColor(vessel.compliance_status) }]}>
                                        <Text style={styles.statusText}>{vessel.compliance_status}</Text>
                                    </View>
                                </View>
                                <View style={styles.vesselInfo}>
                                    <Text style={styles.infoText}>Bioincrustação: {vessel.fouling_mm.toFixed(2)} mm</Text>
                                    <Text style={styles.infoText}>Rugosidade: {vessel.roughness_um.toFixed(0)} µm</Text>
                                </View>
                            </TouchableOpacity>
                        ))}
                    </>
                )}
            </ScrollView>
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
    title: {
        fontSize: 20,
        fontWeight: 'bold',
        color: '#0070f3',
    },
    logoutButton: {
        padding: 8,
    },
    logoutText: {
        color: '#d32f2f',
        fontWeight: '600',
    },
    content: {
        padding: 16,
    },
    sectionTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#333',
        marginBottom: 12,
        marginTop: 8,
    },
    menuContainer: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        marginBottom: 16,
    },
    menuButton: {
        backgroundColor: '#fff',
        padding: 12,
        borderRadius: 8,
        width: '31%',
        alignItems: 'center',
        elevation: 2,
    },
    menuButtonText: {
        fontWeight: '600',
        color: '#0070f3',
        fontSize: 12,
    },
    kpiContainer: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        justifyContent: 'space-between',
        marginBottom: 16,
    },
    vesselCard: {
        backgroundColor: '#fff',
        borderRadius: 12,
        padding: 16,
        marginBottom: 12,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.1,
        shadowRadius: 2,
        elevation: 2,
    },
    vesselHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 8,
    },
    vesselName: {
        fontSize: 16,
        fontWeight: 'bold',
        color: '#333',
    },
    statusBadge: {
        paddingHorizontal: 8,
        paddingVertical: 4,
        borderRadius: 12,
    },
    statusText: {
        color: '#fff',
        fontSize: 10,
        fontWeight: 'bold',
        textTransform: 'uppercase',
    },
    vesselInfo: {
        flexDirection: 'row',
        justifyContent: 'space-between',
    },
    infoText: {
        fontSize: 12,
        color: '#666',
    },
});
