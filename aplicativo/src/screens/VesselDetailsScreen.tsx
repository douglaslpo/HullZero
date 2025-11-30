import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, ActivityIndicator, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { vesselService } from '../api/services';

export default function VesselDetailsScreen({ route, navigation }: any) {
    const { vesselId } = route.params;
    const [vessel, setVessel] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchVessel = async () => {
            try {
                const data = await vesselService.getById(vesselId);
                setVessel(data);
            } catch (error) {
                console.error('Erro ao buscar detalhes:', error);
            } finally {
                setLoading(false);
            }
        };
        fetchVessel();
    }, [vesselId]);

    if (loading) {
        return (
            <View style={styles.loadingContainer}>
                <ActivityIndicator size="large" color="#0070f3" />
            </View>
        );
    }

    return (
        <SafeAreaView style={styles.container}>
            <View style={styles.header}>
                <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
                    <Text style={styles.backText}>← Voltar</Text>
                </TouchableOpacity>
                <Text style={styles.title}>{vessel?.name || 'Detalhes'}</Text>
                <View style={{ width: 50 }} />
            </View>

            <ScrollView contentContainerStyle={styles.content}>
                <View style={styles.card}>
                    <Text style={styles.sectionTitle}>Informações Gerais</Text>
                    <View style={styles.row}>
                        <Text style={styles.label}>IMO:</Text>
                        <Text style={styles.value}>{vessel?.imo_number}</Text>
                    </View>
                    <View style={styles.row}>
                        <Text style={styles.label}>Tipo:</Text>
                        <Text style={styles.value}>{vessel?.vessel_type}</Text>
                    </View>
                    <View style={styles.row}>
                        <Text style={styles.label}>Status:</Text>
                        <Text style={styles.value}>{vessel?.status}</Text>
                    </View>
                </View>

                <View style={styles.card}>
                    <Text style={styles.sectionTitle}>Dimensões</Text>
                    <View style={styles.row}>
                        <Text style={styles.label}>Comprimento:</Text>
                        <Text style={styles.value}>{vessel?.length_m} m</Text>
                    </View>
                    <View style={styles.row}>
                        <Text style={styles.label}>Largura:</Text>
                        <Text style={styles.value}>{vessel?.width_m} m</Text>
                    </View>
                    <View style={styles.row}>
                        <Text style={styles.label}>Calado:</Text>
                        <Text style={styles.value}>{vessel?.draft_m} m</Text>
                    </View>
                </View>
            </ScrollView>
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f0f2f5',
    },
    loadingContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
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
    backButton: {
        padding: 8,
    },
    backText: {
        color: '#0070f3',
        fontSize: 16,
    },
    title: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#333',
    },
    content: {
        padding: 16,
    },
    card: {
        backgroundColor: '#fff',
        borderRadius: 12,
        padding: 16,
        marginBottom: 16,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.1,
        shadowRadius: 2,
        elevation: 2,
    },
    sectionTitle: {
        fontSize: 16,
        fontWeight: 'bold',
        marginBottom: 12,
        color: '#333',
        borderBottomWidth: 1,
        borderBottomColor: '#eee',
        paddingBottom: 8,
    },
    row: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        marginBottom: 8,
    },
    label: {
        color: '#666',
        fontSize: 14,
    },
    value: {
        fontWeight: '600',
        color: '#333',
        fontSize: 14,
    },
});
