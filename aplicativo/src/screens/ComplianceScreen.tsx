import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { complianceService } from '../api/services';
import KPICard from '../components/KPICard';

export default function ComplianceScreen({ navigation }: any) {
    const [summary, setSummary] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            const data = await complianceService.getComplianceSummary();
            setSummary(data);
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <SafeAreaView style={styles.container}>
            <View style={styles.header}>
                <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
                    <Text style={styles.backText}>← Voltar</Text>
                </TouchableOpacity>
                <Text style={styles.title}>Conformidade NORMAM</Text>
                <View style={{ width: 50 }} />
            </View>

            {loading ? (
                <ActivityIndicator size="large" color="#0070f3" style={{ marginTop: 20 }} />
            ) : (
                <ScrollView contentContainerStyle={styles.content}>
                    <View style={styles.kpiContainer}>
                        <KPICard
                            label="Taxa Global"
                            value={`${summary?.compliance_rate_percent?.toFixed(0) || 0}%`}
                            color="#2e7d32"
                        />
                        <KPICard
                            label="Embarcações OK"
                            value={summary?.compliant_vessels || 0}
                            color="#009688"
                        />
                        <KPICard
                            label="Em Alerta"
                            value={summary?.warning_vessels || 0}
                            color="#ed6c02"
                        />
                        <KPICard
                            label="Críticas"
                            value={summary?.critical_vessels || 0}
                            color="#d32f2f"
                        />
                    </View>

                    <View style={styles.infoCard}>
                        <Text style={styles.infoTitle}>Sobre a NORMAM 401</Text>
                        <Text style={styles.infoText}>
                            A NORMAM 401 estabelece os limites aceitáveis de bioincrustação para garantir a eficiência operacional e minimizar o risco de transporte de espécies invasoras.
                        </Text>
                    </View>
                </ScrollView>
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
    content: { padding: 16 },
    kpiContainer: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        justifyContent: 'space-between',
        marginBottom: 16,
    },
    infoCard: {
        backgroundColor: '#fff',
        padding: 16,
        borderRadius: 12,
        elevation: 2,
    },
    infoTitle: { fontSize: 16, fontWeight: 'bold', marginBottom: 8, color: '#333' },
    infoText: { color: '#666', lineHeight: 22 },
});
