import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

interface KPICardProps {
    label: string;
    value: string | number;
    helpText?: string;
    color?: string;
}

export default function KPICard({ label, value, helpText, color = '#0070f3' }: KPICardProps) {
    return (
        <View style={[styles.card, { borderLeftColor: color }]}>
            <Text style={styles.label}>{label}</Text>
            <Text style={[styles.value, { color }]}>{value}</Text>
            {helpText && <Text style={styles.helpText}>{helpText}</Text>}
        </View>
    );
}

const styles = StyleSheet.create({
    card: {
        backgroundColor: '#fff',
        padding: 16,
        borderRadius: 8,
        marginBottom: 12,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.1,
        shadowRadius: 2,
        elevation: 2,
        borderLeftWidth: 4,
        width: '48%', // Para caber 2 por linha
    },
    label: {
        fontSize: 12,
        color: '#666',
        marginBottom: 4,
        fontWeight: '600',
    },
    value: {
        fontSize: 18,
        fontWeight: 'bold',
    },
    helpText: {
        fontSize: 10,
        color: '#999',
        marginTop: 4,
    },
});
