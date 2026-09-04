import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistemaamigos.settings')
django.setup()


from django.contrib.auth.models import User
from django.test import RequestFactory
from unittest.mock import patch
from apps.core.permissions import registrar_auditoria
from apps.core.models import Auditoria, Grupo, Subgrupo
from apps.auditoria.views import listar_auditoria
from apps.dashboard.views import dashboard


def run_tests():
    superuser = User.objects.filter(is_superuser=True).first()
    admin_grupo = User.objects.filter(userprofile__rol='administrador_grupo').first()
    admin_subgrupo = User.objects.filter(userprofile__rol='administrador_subgrupo').first()

    g1 = admin_grupo.userprofile.grupo
    sg1 = admin_subgrupo.userprofile.subgrupo

    # Crear acciones de prueba
    registrar_auditoria(superuser, 'act_superadmin', 'Test General')
    registrar_auditoria(admin_grupo, 'act_grupo', 'Test Grupo', grupo=g1)
    registrar_auditoria(admin_subgrupo, 'act_subgrupo', 'Test Subgrupo', grupo=g1, subgrupo=sg1)

    rf = RequestFactory()

    with patch('apps.auditoria.views.render') as mock_aud_render:
        # TEST 1: Subgrupo admin solo ve de él
        req1 = rf.get('/auditoria/')
        req1.user = admin_subgrupo
        listar_auditoria(req1)
        ctx1 = mock_aud_render.call_args[0][2]
        regs1 = [r.accion for r in ctx1['registros']]
        print('1. Subgrupo admin acciones visibles:', regs1)
        assert 'act_subgrupo' in regs1, "Subgrupo admin debe ver su propia acción"
        assert 'act_grupo' not in regs1, "Subgrupo admin NO debe ver acción de grupo admin"
        assert 'act_superadmin' not in regs1, "Subgrupo admin NO debe ver acción de superadmin"
        print('-> TEST 1 PASSED: Subgrupo admin solo ve su propio historial.\n')

        # TEST 2: Grupo admin ve de él y de sus subgrupos
        req2 = rf.get('/auditoria/')
        req2.user = admin_grupo
        listar_auditoria(req2)
        ctx2 = mock_aud_render.call_args[0][2]
        regs2 = [r.accion for r in ctx2['registros']]
        print('2. Grupo admin acciones visibles (todos):', regs2)
        assert 'act_grupo' in regs2, "Grupo admin debe ver su propia acción"
        assert 'act_subgrupo' in regs2, "Grupo admin debe ver acción de sus subgrupos"
        assert 'act_superadmin' not in regs2, "Grupo admin NO debe ver acción de superadmin"
        print('-> TEST 2 PASSED: Grupo admin ve de él y de sus subgrupos.\n')

        # TEST 3: Grupo admin filtra solo mis cambios
        req3 = rf.get('/auditoria/?origen=mis_cambios')
        req3.user = admin_grupo
        listar_auditoria(req3)
        ctx3 = mock_aud_render.call_args[0][2]
        regs3 = [r.accion for r in ctx3['registros']]
        print('3. Grupo admin filtro mis_cambios:', regs3)
        assert 'act_grupo' in regs3 and 'act_subgrupo' not in regs3
        print('-> TEST 3 PASSED: Grupo admin filtra solo sus propios cambios.\n')

        # TEST 4: Grupo admin filtra solo subgrupos
        req4 = rf.get('/auditoria/?origen=subgrupos')
        req4.user = admin_grupo
        listar_auditoria(req4)
        ctx4 = mock_aud_render.call_args[0][2]
        regs4 = [r.accion for r in ctx4['registros']]
        print('4. Grupo admin filtro subgrupos:', regs4)
        assert 'act_subgrupo' in regs4 and 'act_grupo' not in regs4
        print('-> TEST 4 PASSED: Grupo admin filtra solo cambios de subgrupos.\n')

        # TEST 5: Superadmin ve su historial, de grupos y de subgrupos
        req5 = rf.get('/auditoria/')
        req5.user = superuser
        listar_auditoria(req5)
        ctx5 = mock_aud_render.call_args[0][2]
        regs5 = [r.accion for r in ctx5['registros']]
        print('5. Superadmin acciones visibles:', regs5)
        assert 'act_superadmin' in regs5 and 'act_grupo' in regs5 and 'act_subgrupo' in regs5
        print('-> TEST 5 PASSED: Superadmin ve historial de todos.\n')

    with patch('apps.dashboard.views.render') as mock_dash_render:
        # TEST 6: Dashboard para Superadmin (Múltiples gráficos)
        req6 = rf.get('/dashboard/')
        req6.user = superuser
        dashboard(req6)
        ctx6 = mock_dash_render.call_args[0][2]
        charts6 = ctx6['graficos']
        print('6. Dashboard Gráficos generados:', list(charts6.keys()))
        expected_charts = ['pagos', 'souvenirs', 'sexo', 'estados', 'edades', 'distribucion', 'modalidades', 'tendencia', 'radar']
        for ec in expected_charts:
            assert ec in charts6, f"Falta gráfico {ec} en el dashboard"
        print('-> TEST 6 PASSED: Dashboard superadmin contiene todos los gráficos (pastel, barras, rosquilla, polar, línea, radar).\n')

        # TEST 7: Dashboard para Admin de Grupo
        req7 = rf.get('/dashboard/')
        req7.user = admin_grupo
        dashboard(req7)
        ctx7 = mock_dash_render.call_args[0][2]
        print('7. Grupo admin dashboard total danzarines:', ctx7['total_danzarines'])
        print('-> TEST 7 PASSED: Dashboard admin de grupo restringido a su grupo.\n')

        # TEST 8: Dashboard para Admin de Subgrupo
        req8 = rf.get('/dashboard/')
        req8.user = admin_subgrupo
        dashboard(req8)
        ctx8 = mock_dash_render.call_args[0][2]
        print('8. Subgrupo admin dashboard total danzarines:', ctx8['total_danzarines'])
        print('-> TEST 8 PASSED: Dashboard admin de subgrupo restringido a su subgrupo.\n')

    print('========================================================================')
    print('>>> TODOS LOS TESTS AUTOMATIZADOS (8/8) COMPLETADOS EXITOSAMENTE <<<')
    print('========================================================================')


if __name__ == '__main__':
    run_tests()
